import {
  ArrowLeft,
  Calendar, Clock,
  ExternalLink,
  Loader,
  Tag,
  Upload,
  Video as VideoIcon,
  X,
  Youtube
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { videosApi, youtubeApi } from '../api';

function VideoDetailPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadVideoDetails();
  }, [videoId]);

  const loadVideoDetails = async () => {
    try {
      setLoading(true);
      const response = await videosApi.getVideoDetails(videoId);
      setVideo(response.data);
    } catch (error) {
      console.error('Error loading video details:', error);
      alert('Erreur lors du chargement des détails');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadToYouTube = async () => {
    if (!window.confirm('Uploader cette vidéo sur YouTube ?')) return;

    try {
      setUploading(true);
      const response = await youtubeApi.uploadVideo(video.id, {
        title: video.title,
        description: video.description || `Vidéo: ${video.title}`,
        tags: video.tags || ['video']
      });

      alert('🎉 Vidéo uploadée sur YouTube avec succès !');
      window.open(response.data.youtube_url, '_blank');
      await loadVideoDetails();
    } catch (error) {
      console.error('Error uploading to YouTube:', error);
      alert('Erreur lors de l\'upload: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleUnschedule = async () => {
    if (!window.confirm('Supprimer la planification de cette vidéo ?')) return;
    
    try {
      await youtubeApi.unscheduleVideo(video.id);
      alert('✅ Planification supprimée !');
      await loadVideoDetails();
    } catch (error) {
      console.error('Error unscheduling:', error);
      alert('Erreur lors de la suppression: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = () => {
    if (!video) return null;

    const statusConfig = {
      published: {
        label: 'Publiée sur YouTube',
        className: 'bg-green-100 text-green-800',
        icon: Youtube
      },
      scheduled: {
        label: 'Planifiée',
        className: 'bg-orange-100 text-orange-800',
        icon: Calendar
      },
      draft: {
        label: 'Brouillon',
        className: 'bg-blue-100 text-blue-800',
        icon: VideoIcon
      },
      error: {
        label: 'Erreur',
        className: 'bg-red-100 text-red-800',
        icon: X
      }
    };

    const status = statusConfig[video.publication_status] || statusConfig.draft;
    const Icon = status.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${status.className}`}>
        <Icon className="h-4 w-4 mr-2" />
        {status.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!video) {
    return (
      <div className="text-center py-12">
        <VideoIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Vidéo non trouvée</h3>
      </div>
    );
  }

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'stoicisme-backend.manga-pics.com';

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header avec bouton retour */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/videos')}
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Retour aux vidéos
        </button>
      </div>

      {/* Titre et statut */}
      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{video.title}</h1>
            <div className="flex items-center space-x-3">
              {getStatusBadge()}
              <span className="text-sm text-gray-500">
                <Clock className="h-4 w-4 inline mr-1" />
                {formatDuration(video.duration_seconds)}
              </span>
              <span className="text-sm text-gray-500">
                {video.video_type === 'short' ? '9:16 (Short)' : '16:9 (Normal)'}
              </span>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-2">
            {!video.youtube_video_id && !video.is_scheduled && (
              <button
                onClick={handleUploadToYouTube}
                disabled={uploading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
              >
                {uploading ? (
                  <>
                    <Loader className="h-4 w-4 mr-2 animate-spin" />
                    Upload...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload sur YouTube
                  </>
                )}
              </button>
            )}
            
            {video.is_scheduled && !video.youtube_video_id && (
              <button
                onClick={handleUnschedule}
                className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
              >
                <X className="h-4 w-4 mr-2" />
                Annuler planification
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne principale - Vidéo */}
        <div className="lg:col-span-2 space-y-6">
          {/* Lecteur vidéo */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <video
              controls
              className="w-full"
              poster={video.thumbnail_url ? `${BACKEND_URL}${video.thumbnail_url}` : undefined}
              src={video.video_url ? `${BACKEND_URL}${video.video_url}` : undefined}
            >
              Votre navigateur ne supporte pas la lecture de vidéos.
            </video>
          </div>

          {/* Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">
              {video.description || 'Aucune description'}
            </p>
          </div>

          {/* Tags */}
          {video.tags && video.tags.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Tag className="h-5 w-5 mr-2" />
                Tags
              </h2>
              <div className="flex flex-wrap gap-2">
                {video.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Script associé */}
          {video.script && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Script</h2>
              <h3 className="font-medium text-gray-700 mb-2">{video.script.title}</h3>
              <p className="text-gray-600 text-sm whitespace-pre-wrap line-clamp-6">
                {video.script.original_script}
              </p>
            </div>
          )}
        </div>

        {/* Colonne latérale - Informations */}
        <div className="space-y-6">
          {/* Informations YouTube */}
          {video.youtube_url && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">YouTube</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-500">ID Vidéo</p>
                  <p className="text-sm text-gray-900 font-mono">{video.youtube_video_id}</p>
                </div>
                <div>
                  <a
                    href={video.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink className="h-4 w-4 mr-1" />
                    Voir sur YouTube
                  </a>
                </div>
                {video.uploaded_at && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Uploadée le</p>
                    <p className="text-sm text-gray-900">
                      {new Date(video.uploaded_at).toLocaleString('fr-FR')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Planification */}
          {video.is_scheduled && video.scheduled_publish_date && (
            <div className="bg-orange-50 rounded-lg shadow p-6 border border-orange-200">
              <h2 className="text-lg font-semibold text-orange-900 mb-4 flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Planification
              </h2>
              <div>
                <p className="text-sm font-medium text-orange-700">Date de publication</p>
                <p className="text-lg font-semibold text-orange-900 mt-1">
                  {new Date(video.scheduled_publish_date).toLocaleString('fr-FR', {
                    dateStyle: 'full',
                    timeStyle: 'short'
                  })}
                </p>
              </div>
            </div>
          )}

          {/* Erreur de publication */}
          {video.publication_error && (
            <div className="bg-red-50 rounded-lg shadow p-6 border border-red-200">
              <h2 className="text-lg font-semibold text-red-900 mb-2 flex items-center">
                <X className="h-5 w-5 mr-2" />
                Erreur de publication
              </h2>
              <p className="text-sm text-red-700">{video.publication_error}</p>
              {video.publication_error_at && (
                <p className="text-xs text-red-600 mt-2">
                  {new Date(video.publication_error_at).toLocaleString('fr-FR')}
                </p>
              )}
            </div>
          )}

          {/* Métadonnées */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Métadonnées</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-500">ID</p>
                <p className="text-sm text-gray-900 font-mono break-all">{video.id}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Créée le</p>
                <p className="text-sm text-gray-900">
                  {new Date(video.created_at).toLocaleString('fr-FR')}
                </p>
              </div>
              {video.idea && (
                <div>
                  <p className="text-sm font-medium text-gray-500">Idée</p>
                  <p className="text-sm text-gray-900">{video.idea.title}</p>
                  {video.idea.keywords && video.idea.keywords.length > 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      Mots-clés: {video.idea.keywords.join(', ')}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VideoDetailPage;
