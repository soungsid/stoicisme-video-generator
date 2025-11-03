import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from database import get_config_collection
from datetime import datetime, timedelta
import json

class YouTubeService:
    """
    Service pour gérer l'upload de vidéos sur YouTube
    """
    
    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8001/api/youtube/oauth/callback")
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    
    def get_authorization_url(self) -> str:
        """Générer l'URL d'authentification OAuth"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    async def handle_oauth_callback(self, code: str):
        """Gérer le callback OAuth et sauvegarder les tokens"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Sauvegarder les tokens en base de données
        config_collection = get_config_collection()
        await config_collection.update_one(
            {"type": "youtube"},
            {
                "$set": {
                    "type": "youtube",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "access_token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_expiry": datetime.now() + timedelta(seconds=credentials.expiry.timestamp() - datetime.now().timestamp()) if credentials.expiry else None,
                    "is_authenticated": True
                }
            },
            upsert=True
        )
        
        print("✅ YouTube OAuth tokens saved")
    
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
    
    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "22",
        privacy_status: str = "public"
    ) -> tuple:
        """
        Uploader une vidéo sur YouTube
        Retourne: (video_id, video_url)
        """
        try:
            credentials = await self._get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✅ Video uploaded to YouTube: {video_url}")
            return video_id, video_url
            
        except Exception as e:
            print(f"❌ Error uploading to YouTube: {str(e)}")
            raise
