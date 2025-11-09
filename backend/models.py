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
    VALIDATED = "validated"
    QUEUED = "queued"  # NEW: En attente dans la queue
    PROCESSING = "processing"  # NEW: En cours de traitement
    SCRIPT_GENERATING = "script_generating"
    SCRIPT_GENERATED = "script_generated"
    SCRIPT_ADAPTING = "script_adapting"
    SCRIPT_ADAPTED = "script_adapted"
    AUDIO_GENERATING = "audio_generating"
    AUDIO_GENERATED = "audio_generated"
    VIDEO_GENERATING = "video_generating"
    VIDEO_GENERATED = "video_generated"
    UPLOADED = "uploaded"
    REJECTED = "rejected"
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
    status: IdeaStatus = IdeaStatus.PENDING
    error_message: Optional[str] = None
    progress_percentage: int = 0
    current_step: Optional[str] = None
    last_successful_step: Optional[str] = None  # Dernière étape réussie avant erreur
    created_at: datetime = Field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None
    
class Script(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    title: str
    original_script: str
    elevenlabs_adapted_script: Optional[str] = None
    phrases: Optional[List[str]] = []
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
    thumbnail_path: Optional[str] = None
    duration_seconds: float
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class VideoJob(BaseModel):
    """Job de génération vidéo dans la queue"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    status: JobStatus = JobStatus.QUEUED
    start_from: str = "script"  # script, adapt, audio, video
    priority: int = 0  # Plus élevé = plus prioritaire
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

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

class CustomScriptRequest(BaseModel):
    script_text: str = Field(..., min_length=50)
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
