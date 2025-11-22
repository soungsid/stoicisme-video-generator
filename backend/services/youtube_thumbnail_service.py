import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from database import get_config_collection, get_videos_collection
from helpers.datetime_utils import now_utc
import traceback
from typing import Optional

class YouTubeThumbnailService:
    """
    Service pour gérer la mise à jour des thumbnails sur YouTube via l'API v3
    """
    
    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "1003461788594-hrti4l1lueto52iua8levktl7urdnjjd.apps.googleusercontent.com")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "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")
        self.scopes = [
            'openid',  
            'https://www.googleapis.com/auth/userinfo.email', 
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
    
    async def _get_credentials(self) -> Credentials:
        """Récupérer les credentials depuis la base de données"""
        config_collection = get_config_collection()
        config = await config_collection.find_one({"type": "youtube"})
        
        if not config or not config.get("is_authenticated"):
            raise ValueError("YouTube not authenticated. Please complete OAuth flow first.")
        
        credentials = Credentials(
            token=config["access_token"],
            refresh_token=config.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes
        )
        
        # Rafraîchir le token si nécessaire
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            
            # Mettre à jour le token en base
            await config_collection.update_one(
                {"type": "youtube"},
                {"$set": {"access_token": credentials.token}}
            )
        
        return credentials
    
    async def update_thumbnail(
        self, 
        youtube_video_id: str, 
        thumbnail_path: str
    ) -> dict:
        """
        Mettre à jour le thumbnail d'une vidéo YouTube
        
        Args:
            youtube_video_id: ID de la vidéo YouTube
            thumbnail_path: Chemin vers le fichier thumbnail
            
        Returns:
            dict avec les informations de mise à jour
            
        Raises:
            ValueError: Si le fichier thumbnail n'existe pas
            Exception: Pour les autres erreurs d'API
        """
        try:
            # Vérifier que le fichier thumbnail existe
            if not os.path.exists(thumbnail_path):
                raise ValueError(f"Thumbnail file not found: {thumbnail_path}")
            
            # Vérifier que le fichier est une image valide
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
            file_ext = os.path.splitext(thumbnail_path)[1].lower()
            if file_ext not in valid_extensions:
                raise ValueError(f"Invalid thumbnail format. Supported formats: {', '.join(valid_extensions)}")
            
            # Récupérer les credentials
            credentials = await self._get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Préparer le média pour l'upload
            media = MediaFileUpload(
                thumbnail_path,
                mimetype=f'image/{file_ext[1:]}',  # jpg -> image/jpeg, png -> image/png
                resumable=True
            )
            
            # Mettre à jour le thumbnail via l'API YouTube
            request = youtube.thumbnails().set(
                videoId=youtube_video_id,
                media_body=media
            )
            
            response = request.execute()
            
            print(f"✅ Thumbnail updated for video {youtube_video_id}")
            
            return {
                "success": True,
                "youtube_video_id": youtube_video_id,
                "thumbnail_url": response.get("items", [{}])[0].get("default", {}).get("url", ""),
                "updated_at": now_utc().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error updating thumbnail for video {youtube_video_id}: {str(e)}")
            traceback.print_exc()
            raise
    
    async def update_thumbnail_by_video_id(
        self, 
        video_id: str
    ) -> dict:
        """
        Mettre à jour le thumbnail d'une vidéo YouTube en utilisant l'ID de la vidéo locale
        
        Args:
            video_id: ID de la vidéo dans la base de données
            
        Returns:
            dict avec les informations de mise à jour
            
        Raises:
            ValueError: Si la vidéo n'a pas de thumbnail_path ou de youtube_video_id
        """
        try:
            # Récupérer la vidéo depuis la base de données
            videos_collection = get_videos_collection()
            video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
            
            if not video:
                raise ValueError(f"Video {video_id} not found in database")
            
            youtube_video_id = video.get("youtube_video_id")
            thumbnail_path = video.get("thumbnail_path")
            
            if not youtube_video_id:
                raise ValueError(f"Video {video_id} has no YouTube video ID")
            
            if not thumbnail_path:
                raise ValueError(f"Video {video_id} has no thumbnail path")
            
            # Mettre à jour le thumbnail
            result = await self.update_thumbnail(youtube_video_id, thumbnail_path)
            
            return result
            
        except Exception as e:
            print(f"❌ Error updating thumbnail for local video {video_id}: {str(e)}")
            raise
    
    async def get_thumbnail_info(self, youtube_video_id: str) -> dict:
        """
        Récupérer les informations sur les thumbnails d'une vidéo YouTube
        
        Args:
            youtube_video_id: ID de la vidéo YouTube
            
        Returns:
            dict avec les URLs des thumbnails disponibles
        """
        try:
            credentials = await self._get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Récupérer les informations de la vidéo
            video_response = youtube.videos().list(
                part='snippet',
                id=youtube_video_id
            ).execute()
            
            if not video_response.get('items'):
                raise ValueError(f"Video {youtube_video_id} not found")
            
            snippet = video_response['items'][0]['snippet']
            thumbnails = snippet.get('thumbnails', {})
            
            return {
                "youtube_video_id": youtube_video_id,
                "thumbnails": thumbnails,
                "default_thumbnail": thumbnails.get('default', {}).get('url', ''),
                "medium_thumbnail": thumbnails.get('medium', {}).get('url', ''),
                "high_thumbnail": thumbnails.get('high', {}).get('url', ''),
                "standard_thumbnail": thumbnails.get('standard', {}).get('url', ''),
                "maxres_thumbnail": thumbnails.get('maxres', {}).get('url', '')
            }
            
        except Exception as e:
            print(f"❌ Error getting thumbnail info for video {youtube_video_id}: {str(e)}")
            raise
    
    async def batch_update_thumbnails(self, video_ids: list) -> dict:
        """
        Mettre à jour les thumbnails de plusieurs vidéos en lot
        
        Args:
            video_ids: Liste des IDs de vidéos locales
            
        Returns:
            dict avec les résultats de chaque mise à jour
        """
        try:
            results = {
                "successful": [],
                "failed": [],
                "total": len(video_ids)
            }
            
            for video_id in video_ids:
                try:
                    result = await self.update_thumbnail_by_video_id(video_id)
                    results["successful"].append({
                        "video_id": video_id,
                        "result": result
                    })
                    print(f"✅ Thumbnail updated for video {video_id}")
                except Exception as e:
                    results["failed"].append({
                        "video_id": video_id,
                        "error": str(e)
                    })
                    print(f"❌ Failed to update thumbnail for video {video_id}: {str(e)}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in batch thumbnail update: {str(e)}")
            raise
