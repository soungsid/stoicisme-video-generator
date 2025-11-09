import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from database import get_config_collection
from datetime import datetime, timedelta
import json
import traceback

class YouTubeService:
    """
    Service pour gérer l'upload de vidéos sur YouTube
    """
    
    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "1003461788594-hrti4l1lueto52iua8levktl7urdnjjd.apps.googleusercontent.com")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "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")
        self.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8001/api/youtube/oauth/callback")
        self.scopes = [
            'openid',  
            'https://www.googleapis.com/auth/userinfo.email', 
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
    

    def get_authorization_url(self) -> str:
        """Générer l'URL d'authentification OAuth"""
        try:
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            print("📁 Loaded env vars:")
            print(f"CLIENT_ID: {self.client_id}")
            print(f"REDIRECT_URI: {self.redirect_uri}")
            print(f"SCOPES: {self.scopes}")
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

        except Exception as e:
            print("❌ Error generating authorization URL:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise e  # ou `raise` pour relancer l’erreur originale proprement

    
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
        print("creation client flow")
        flow = Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        print("flow fetch_token")

        flow.fetch_token(code=code)
        credentials = flow.credentials
        print("flow get credential")
        
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
    
    async def get_channel_info(self) -> dict:
        """
        Récupérer les informations de la chaîne YouTube connectée
        """
        try:
            credentials = await self._get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Récupérer les infos de la chaîne
            request = youtube.channels().list(
                part='snippet,statistics,brandingSettings,contentDetails',
                mine=True
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError("No channel found for this account")
            
            channel = response['items'][0]
            
            # Essayer de récupérer l'email via l'API OAuth2
            email = 'N/A'
            verified_email = False
            try:
                from googleapiclient.discovery import build as google_build
                oauth2_service = google_build('oauth2', 'v2', credentials=credentials)
                user_info = oauth2_service.userinfo().get().execute()
                email = user_info.get('email', 'N/A')
                verified_email = user_info.get('verified_email', False)
            except Exception as email_error:
                # Si l'email n'est pas accessible, on continue sans
                print(f"⚠️  Could not retrieve email: {email_error}")
            
            channel_info = {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'custom_url': channel['snippet'].get('customUrl', ''),
                'published_at': channel['snippet']['publishedAt'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0)),
                'country': channel['snippet'].get('country', ''),
                'email': email,
                'verified_email': verified_email,
                'hidden_subscriber_count': channel['statistics'].get('hiddenSubscriberCount', False),
            }
            
            print(f"✅ Channel info retrieved: {channel_info['title']} ({channel_info['email']})")
            return channel_info
            
        except Exception as e:
            print(f"❌ Error getting channel info: {str(e)}")
            raise
    
    async def update_video_metadata(
        self,
        youtube_video_id: str,
        title: str = None,
        description: str = None,
        tags: list = None
    ) -> dict:
        """
        Mettre à jour les métadonnées d'une vidéo YouTube
        """
        try:
            credentials = await self._get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Récupérer d'abord les infos actuelles de la vidéo
            video_response = youtube.videos().list(
                part='snippet',
                id=youtube_video_id
            ).execute()
            
            if not video_response.get('items'):
                raise ValueError(f"Video {youtube_video_id} not found")
            
            current_snippet = video_response['items'][0]['snippet']
            
            # Mettre à jour seulement les champs fournis
            update_snippet = {
                'categoryId': current_snippet['categoryId'],
                'title': title if title is not None else current_snippet['title'],
                'description': description if description is not None else current_snippet['description'],
                'tags': tags if tags is not None else current_snippet.get('tags', [])
            }
            
            # Effectuer la mise à jour
            update_response = youtube.videos().update(
                part='snippet',
                body={
                    'id': youtube_video_id,
                    'snippet': update_snippet
                }
            ).execute()
            
            print(f"✅ Video {youtube_video_id} metadata updated")
            return {
                'video_id': youtube_video_id,
                'title': update_snippet['title'],
                'description': update_snippet['description'],
                'tags': update_snippet['tags']
            }
            
        except Exception as e:
            print(f"❌ Error updating video metadata: {str(e)}")
            raise
    
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
