import sys
import os

# Ajouter le répertoire parent (stoicisme-video-generator) au path pour les imports absolus
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from models import IdeaStatus, JobStatus, VideoJob, VideoIdea, Script, AudioGeneration, Video
from services.queue_service import QueueService
from workers.video_worker import VideoWorker
from database import get_ideas_collection, get_queue_collection, get_scripts_collection, get_audio_generations_collection, get_videos_collection


@pytest.fixture
def mock_db_collections():
    """Fixture pour mocker les collections de la base de données"""
    with patch('backend.database.get_ideas_collection', new_callable=AsyncMock) as mock_ideas, \
         patch('backend.database.get_queue_collection', new_callable=AsyncMock) as mock_queue, \
         patch('backend.database.get_scripts_collection', new_callable=AsyncMock) as mock_scripts, \
         patch('backend.database.get_audio_generations_collection', new_callable=AsyncMock) as mock_audios, \
         patch('backend.database.get_videos_collection', new_callable=AsyncMock) as mock_videos:
        
        # Mocks pour find_one
        mock_ideas.find_one.return_value = None
        mock_queue.find_one.return_value = None
        mock_scripts.find_one.return_value = None
        mock_audios.find_one.return_value = None
        mock_videos.find_one.return_value = None

        yield {
            "ideas": mock_ideas,
            "queue": mock_queue,
            "scripts": mock_scripts,
            "audios": mock_audios,
            "videos": mock_videos
        }

@pytest.fixture
def mock_services():
    """Fixture pour mocker les services externes"""
    with patch('backend.services.script_service.ScriptService', new_callable=AsyncMock) as mock_script_service, \
         patch('backend.services.audio_service.AudioService', new_callable=AsyncMock) as mock_audio_service, \
         patch('backend.services.video_service.VideoService', new_callable=AsyncMock) as mock_video_service, \
         patch('backend.agents.script_adapter_agent.ScriptAdapterAgent', new_callable=AsyncMock) as mock_adapter_agent:
        
        # S'assurer que les méthodes sont des AsyncMock si elles sont awaitable
        mock_script_service.return_value.generate_script = AsyncMock()
        mock_audio_service.return_value.complete_audio_generation_with_timestamps = AsyncMock()
        mock_video_service.return_value.generate_video = AsyncMock()
        mock_adapter_agent.return_value.adapt_script = AsyncMock(return_value=("Adapted script", ["phrase1", "phrase2"]))

        yield {
            "script": mock_script_service.return_value,
            "audio": mock_audio_service.return_value,
            "video": mock_video_service.return_value,
            "adapter": mock_adapter_agent.return_value
        }

@pytest.fixture
def video_worker(mock_db_collections, mock_services):
    """Fixture pour le VideoWorker"""
    worker = VideoWorker()
    worker.db_client = AsyncMock() # Mock le client pour éviter la vraie connexion
    worker.db = AsyncMock() # Mock la DB
    worker.queue_service = AsyncMock(spec=QueueService) # Mock le QueueService
    worker.script_service = mock_services["script"] # Injecter le mock du script_service
    
    # Remplacer les collections de la DB par les mocks
    worker.db.ideas = mock_db_collections["ideas"]
    worker.db.queue = mock_db_collections["queue"]
    worker.db.scripts = mock_db_collections["scripts"]
    worker.db.audios = mock_db_collections["audios"]
    worker.db.videos = mock_db_collections["videos"]
    
    # Mock des méthodes de QueueService utilisées par le worker
    worker.queue_service.complete_job = AsyncMock()
    worker.queue_service.fail_job = AsyncMock()

    # Patch global des fonctions de base de données pour tous les services
    with patch('backend.database.db', worker.db), \
         patch('backend.database.db_client', worker.db_client), \
         patch('backend.database.get_database', return_value=worker.db), \
         patch('backend.database.get_ideas_collection', return_value=mock_db_collections["ideas"]), \
         patch('backend.database.get_scripts_collection', return_value=mock_db_collections["scripts"]), \
         patch('backend.database.get_audio_generations_collection', return_value=mock_db_collections["audios"]), \
         patch('backend.database.get_videos_collection', return_value=mock_db_collections["videos"]), \
         patch('backend.database.get_queue_collection', return_value=mock_db_collections["queue"]):
        yield worker


@pytest.mark.asyncio
async def test_regenerate_script_only(video_worker, mock_db_collections, mock_services):
    """
    Teste que la régénération de script n'exécute que l'étape de script
    """
    # Arrange
    idea_id = "test_idea_script_regen"
    job_id = "job_script_regen"
    initial_script_content = "An old script content."
    generated_script_content = "A new generated script content."

    # Préparer l'idée existante
    idea = VideoIdea(
        id=idea_id,
        title="Test Idea Script Regen",
        keywords=["regen", "script"],
        status=IdeaStatus.AUDIO_GENERATED, # Supposons que l'audio était déjà généré
        script_id="old_script_id"
    )
    mock_db_collections["ideas"].find_one.side_effect = [idea.model_dump(), idea.model_dump()] # Pour les deux appels dans process_job

    # Préparer le script existant
    old_script = Script(
        id="old_script_id",
        idea_id=idea_id,
        title="Old Script Title",
        original_script=initial_script_content
    )
    mock_db_collections["scripts"].find_one.return_value = old_script.model_dump() # Pour la récupération du script_id
    mock_db_collections["scripts"].update_one.return_value = AsyncMock() # Mock pour update_one

    # Configurer le mock pour le ScriptService
    mock_services["script"].generate_script.return_value = None # Le service met à jour la DB directement

    # Le job de régénération
    regeneration_job = VideoJob(
        job_id=job_id,
        idea_id=idea_id,
        start_from="script",
        is_regeneration=True,
        status=JobStatus.PROCESSING # Le worker s'attend à un job en PROCESSING
    )

    # Act
    await video_worker.process_job(regeneration_job)

    # Assert
    # 1. Vérifier que generate_script a été appelé
    mock_services["script"].generate_script.assert_called_once_with(idea_id)

    # 2. Vérifier que AudioService et VideoService n'ont PAS été appelés
    mock_services["audio"].complete_audio_generation_with_timestamps.assert_not_called()
    mock_services["video"].generate_video.assert_not_called()
    mock_services["adapter"].adapt_script.assert_not_called()

    # 3. Vérifier que le statut de l'idée a été mis à jour correctement
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.SCRIPT_GENERATING}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.SCRIPT_GENERATED}}
    )

    # 4. Vérifier que le job est complété
    video_worker.queue_service.complete_job.assert_called_once_with(job_id)
    video_worker.queue_service.fail_job.assert_not_called()

    print(f"✅ Test regenerate_script_only passed for idea {idea_id}")

@pytest.mark.asyncio
async def test_regenerate_audio_only(video_worker, mock_db_collections, mock_services):
    """
    Teste que la régénération d'audio n'exécute que l'étape d'audio
    """
    # Arrange
    idea_id = "test_idea_audio_regen"
    job_id = "job_audio_regen"
    initial_script_content = "Script content for audio regeneration."
    adapted_script_content = "Adapted script for audio regeneration."

    # Préparer l'idée existante
    idea = VideoIdea(
        id=idea_id,
        title="Test Idea Audio Regen",
        keywords=["regen", "audio"],
        status=IdeaStatus.VIDEO_GENERATED, # Supposons que la vidéo était déjà générée
        script_id="existing_script_id"
    )
    mock_db_collections["ideas"].find_one.side_effect = [idea.model_dump(), idea.model_dump()]

    # Préparer le script existant
    existing_script = Script(
        id="existing_script_id",
        idea_id=idea_id,
        title="Existing Script Title",
        original_script=initial_script_content,
        elevenlabs_adapted_script="Old adapted script",
        phrases=["old phrase 1", "old phrase 2"]
    )
    mock_db_collections["scripts"].find_one.return_value = existing_script.model_dump()
    mock_db_collections["scripts"].update_one.return_value = AsyncMock()

    # Configurer les mocks pour les services
    mock_services["script"].generate_script.return_value = None
    mock_services["audio"].complete_audio_generation_with_timestamps.return_value = AsyncMock() # Simule un objet de retour pour AudioGeneration
    mock_services["adapter"].adapt_script.return_value = (adapted_script_content, ["new phrase 1", "new phrase 2"])

    # Le job de régénération
    regeneration_job = VideoJob(
        job_id=job_id,
        idea_id=idea_id,
        start_from="audio",
        is_regeneration=True,
        status=JobStatus.PROCESSING
    )

    # Act
    await video_worker.process_job(regeneration_job)

    # Assert
    # 1. Vérifier que generate_script n'a PAS été appelé
    mock_services["script"].generate_script.assert_not_called()

    # 2. Vérifier que adapt_script et complete_audio_generation_with_timestamps ont été appelés
    mock_services["adapter"].adapt_script.assert_called_once_with(initial_script_content)
    mock_services["audio"].complete_audio_generation_with_timestamps.assert_called_once_with(existing_script.id)

    # 3. Vérifier que generate_video n'a PAS été appelé
    mock_services["video"].generate_video.assert_not_called()

    # 4. Vérifier les mises à jour de statut
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.AUDIO_GENERATING}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.AUDIO_GENERATED}}
    )

    # 5. Vérifier que le script a été mis à jour avec le contenu adapté
    mock_db_collections["scripts"].update_one.assert_called_once_with(
        {"id": existing_script.id},
        {"$set": {
            "elevenlabs_adapted_script": adapted_script_content,
            "phrases": ["new phrase 1", "new phrase 2"]
        }}
    )

    # 6. Vérifier que le job est complété
    video_worker.queue_service.complete_job.assert_called_once_with(job_id)
    video_worker.queue_service.fail_job.assert_not_called()

    print(f"✅ Test regenerate_audio_only passed for idea {idea_id}")


@pytest.mark.asyncio
async def test_regenerate_video_only(video_worker, mock_db_collections, mock_services):
    """
    Teste que la régénération de vidéo n'exécute que l'étape de vidéo
    """
    # Arrange
    idea_id = "test_idea_video_regen"
    job_id = "job_video_regen"
    script_id = "existing_script_for_video"

    # Préparer l'idée existante (audio déjà généré)
    idea = VideoIdea(
        id=idea_id,
        title="Test Idea Video Regen",
        keywords=["regen", "video"],
        status=IdeaStatus.AUDIO_GENERATED,
        script_id=script_id
    )
    mock_db_collections["ideas"].find_one.side_effect = [idea.model_dump(), idea.model_dump()]

    # Préparer le script existant (audio déjà généré implique script existe)
    existing_script = Script(
        id=script_id,
        idea_id=idea_id,
        title="Existing Script Title",
        original_script="Some script text",
        elevenlabs_adapted_script="Some adapted script",
        phrases=["phrase1", "phrase2"]
    )
    mock_db_collections["scripts"].find_one.return_value = existing_script.model_dump()

    # Configurer les mocks pour les services
    mock_services["script"].generate_script.assert_not_called() # Ne doit pas être appelé
    mock_services["audio"].complete_audio_generation_with_timestamps.assert_not_called() # Ne doit pas être appelé
    mock_services["adapter"].adapt_script.assert_not_called() # Ne doit pas être appelé
    mock_services["video"].generate_video.return_value = AsyncMock() # Simule un objet de retour pour Video

    # Le job de régénération
    regeneration_job = VideoJob(
        job_id=job_id,
        idea_id=idea_id,
        start_from="video",
        is_regeneration=True,
        status=JobStatus.PROCESSING
    )

    # Act
    await video_worker.process_job(regeneration_job)

    # Assert
    # 1. Vérifier que generate_video a été appelé
    mock_services["video"].generate_video.assert_called_once_with(script_id=script_id)

    # 2. Vérifier que les étapes précédentes n'ont PAS été appelées
    mock_services["script"].generate_script.assert_not_called()
    mock_services["audio"].complete_audio_generation_with_timestamps.assert_not_called()
    mock_services["adapter"].adapt_script.assert_not_called()

    # 3. Vérifier les mises à jour de statut
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.VIDEO_GENERATING}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.VIDEO_GENERATED}}
    )

    # 4. Vérifier que le job est complété
    video_worker.queue_service.complete_job.assert_called_once_with(job_id)
    video_worker.queue_service.fail_job.assert_not_called()

    print(f"✅ Test regenerate_video_only passed for idea {idea_id}")


@pytest.mark.asyncio
async def test_full_pipeline_resumption_from_audio(video_worker, mock_db_collections, mock_services):
    """
    Teste la reprise du pipeline complet (non-regeneration) à partir de l'étape audio.
    """
    # Arrange
    idea_id = "test_idea_full_pipeline_resumption"
    job_id = "job_full_pipeline_resumption"
    script_id = "existing_script_id_for_resumption"
    initial_script_content = "Script for full pipeline resumption."
    adapted_script_content = "Adapted script for full pipeline resumption."

    # Préparer l'idée avec un statut indiquant qu'elle est prête pour l'audio
    idea = VideoIdea(
        id=idea_id,
        title="Test Full Pipeline Resumption",
        keywords=["full", "pipeline", "resumption"],
        status=IdeaStatus.SCRIPT_GENERATED, # Le script est déjà généré
        script_id=script_id
    )
    mock_db_collections["ideas"].find_one.side_effect = [idea.model_dump(), idea.model_dump(), idea.model_dump(), idea.model_dump()] # Plusieurs appels

    # Préparer le script existant
    existing_script = Script(
        id=script_id,
        idea_id=idea_id,
        title="Existing Script Title",
        original_script=initial_script_content
    )
    mock_db_collections["scripts"].find_one.return_value = existing_script.model_dump()
    mock_db_collections["scripts"].update_one.return_value = AsyncMock()

    # Configurer les mocks pour les services
    mock_services["script"].generate_script.return_value = None
    mock_services["audio"].complete_audio_generation_with_timestamps.return_value = AsyncMock()
    mock_services["video"].generate_video.return_value = AsyncMock()
    mock_services["adapter"].adapt_script.return_value = (adapted_script_content, ["phrase1", "phrase2"])

    # Le job de pipeline complet (non-régénération)
    pipeline_job = VideoJob(
        job_id=job_id,
        idea_id=idea_id,
        start_from="script", # C'est le start_from initial, mais le worker va le reprendre
        is_regeneration=False,
        status=JobStatus.PROCESSING
    )

    # Act
    await video_worker.process_job(pipeline_job)

    # Assert
    # 1. generate_script ne doit PAS être appelé car le statut initial est SCRIPT_GENERATED
    mock_services["script"].generate_script.assert_not_called()

    # 2. adapt_script, complete_audio_generation_with_timestamps et generate_video DOIVENT être appelés
    mock_services["adapter"].adapt_script.assert_called_once_with(initial_script_content)
    mock_services["audio"].complete_audio_generation_with_timestamps.assert_called_once_with(script_id)
    mock_services["video"].generate_video.assert_called_once_with(script_id=script_id)

    # 3. Vérifier les mises à jour de statut
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.AUDIO_GENERATING}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.AUDIO_GENERATED}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.VIDEO_GENERATING}}
    )
    mock_db_collections["ideas"].update_one.assert_any_call(
        {"id": idea_id},
        {"$set": {"status": IdeaStatus.VIDEO_GENERATED}}
    )

    # 4. Vérifier que le job est complété
    video_worker.queue_service.complete_job.assert_called_once_with(job_id)
    video_worker.queue_service.fail_job.assert_not_called()

    print(f"✅ Test full_pipeline_resumption_from_audio passed for idea {idea_id}")
