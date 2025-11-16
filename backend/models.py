from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class VideoType(str, Enum):
    SHORT = "short"  # 9:16
    NORMAL = "normal"  # 16:9

class IdeaStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SCRIPT_GENERATING = "script_generating"
    SCRIPT_GENERATED = "script_generated"
    AUDIO_GENERATING = "audio_generating"
    AUDIO_GENERATED = "audio_generated"
    VIDEO_GENERATING = "video_generating"
    VIDEO_GENERATED = "video_generated"
    ERROR = "error"

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoIdea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    keywords: List[str] = []
    video_type: VideoType = VideoType.SHORT
    duration_seconds: Optional[int] = 30
    sections_count: Optional[int] = None  # Nombre de sections pour vidéos longues (normal)
    section_titles: Optional[List[str]] = None  # Titres des sections générés
    status: IdeaStatus = IdeaStatus.PENDING
    script_id: Optional[str] = None  # ID du script généré
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
class Script(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    title: str
    original_script: str
    youtube_description: Optional[str] = Field(None, description="Description YouTube générée automatiquement")
    elevenlabs_adapted_script: Optional[str] = None
    phrases: Optional[List[str]] = []
    video_guideline: Optional[str] = Field(None, description="Instructions supplémentaires pour le LLM lors de la génération du script")
    created_at: datetime = Field(default_factory=datetime.now)
    
class AudioPhrase(BaseModel):
    phrase_index: int
    phrase_text: str
    audio_path: str
    duration_ms: int
    start_time_ms: int
    end_time_ms: int

class AudioGeneration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    script_id: str
    idea_id: str
    phrases: List[AudioPhrase] = []
    total_duration_ms: int = 0
    audio_directory: str
    created_at: datetime = Field(default_factory=datetime.now)

class Video(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    script_id: str
    audio_id: str
    title: str
    video_type: VideoType
    video_path: str
    video_relative_path: str
    thumbnail_path: Optional[str] = None
    duration_seconds: float
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    scheduled_publish_date: Optional[datetime] = None
    is_scheduled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    youtube_description: Optional[str] = None

class VideoJob(BaseModel):
    """Job de génération vidéo dans la queue"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    status: JobStatus = JobStatus.QUEUED
    start_from: str = "script"
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 1

class YouTubeConfig(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_authenticated: bool = False

class IdeaGenerationRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=20)
    keywords: Optional[List[str]] = None
    custom_title: Optional[str] = Field(None, description="Titre personnalisé pour l'idée (ex: '5 Habitudes terribles qui ruinent votre matinée!')")
    video_type: VideoType = VideoType.SHORT
    duration_seconds: int = Field(default=30, ge=10, le=600)
    sections_count: Optional[int] = Field(None, ge=2, le=10, description="Nombre de sections pour vidéos longues (type normal)")

class CustomScriptRequest(BaseModel):
    script_text: str = Field(..., min_length=50)
    custom_title: Optional[str] = Field(None, description="Titre optionnel pour le script custom")
    keywords: Optional[List[str]] = None
    video_type: VideoType = VideoType.SHORT
    duration_seconds: int = Field(default=30, ge=10, le=600)

class ScriptGenerationRequest(BaseModel):
    idea_id: str
    duration_seconds: int = Field(default=30, ge=10, le=600)

class ValidateIdeaRequest(BaseModel):
    video_type: VideoType
    duration_seconds: int = Field(ge=10, le=600)
    keywords: Optional[List[str]] = None

# ===== NOUVEAUX MODÈLES POUR LA GESTION YOUTUBE =====

class ScheduleVideoRequest(BaseModel):
    """Requête pour planifier une vidéo"""
    publish_date: str = Field(..., description="Date de publication au format ISO (YYYY-MM-DDTHH:MM:SS)")

class BulkScheduleRequest(BaseModel):
    """Requête pour planifier plusieurs vidéos en masse"""
    start_date: str = Field(..., description="Date de début au format YYYY-MM-DD")
    videos_per_day: int = Field(default=2, ge=1, le=10, description="Nombre de vidéos par jour")
    publish_times: List[str] = Field(..., description="Heures de publication (ex: ['09:00', '18:00'])")

class UploadVideoRequest(BaseModel):
    """Requête pour uploader une vidéo sur YouTube"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category_id: str = Field(default="22", description="ID de catégorie YouTube")
    privacy_status: str = Field(default="public", description="public, private, ou unlisted")

class UpdateVideoMetadataRequest(BaseModel):
    """Requête pour mettre à jour les métadonnées d'une vidéo YouTube"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class UpdateVideoRequest(BaseModel):
    """Requête pour mettre à jour les détails d'une vidéo locale"""
    title: Optional[str] = None
    video_type: Optional[VideoType] = None
    video_path: Optional[str] = None
    video_relative_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    scheduled_publish_date: Optional[datetime] = None
    is_scheduled: Optional[bool] = None

class VideoSection(BaseModel):
    """Représente une section d'une vidéo longue"""
    section_number: int
    title: str
    script: str
    duration_seconds: float
    start_time: float = 0.0
    end_time: float = 0.0
