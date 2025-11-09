import React, { useState, useEffect } from 'react';
import { Video, Loader, Youtube, ExternalLink, Edit, Calendar, Filter } from 'lucide-react';
import { videosApi, youtubeApi } from '../api';
import EditVideoMetadataModal from '../components/EditVideoMetadataModal';
import BulkSchedulerModal from '../components/BulkSchedulerModal';

function VideosPage() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(null);
  const [editingVideo, setEditingVideo] = useState(null);
  const [statusFilter, setStatusFilter] = useState(null);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showScheduler, setShowScheduler] = useState(false);

  useEffect(() => {
    loadVideos();
  }, [statusFilter, sortBy, sortOrder]);

  const loadVideos = async () => {
    try {
      setLoading(true);
      const response = await videosApi.listVideos(statusFilter, sortBy, sortOrder);
      setVideos(response.data);
    } catch (error) {
      console.error('Error loading videos:', error);
      alert('Erreur lors du chargement des vidéos');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadToYouTube = async (video) => {
    if (!window.confirm('Uploader cette vidéo sur YouTube ?')) return;

    try {
      setUploading(video.id);
      const response = await youtubeApi.uploadVideo(video.id, {
        title: video.title,
        description: `Vidéo sur le stoïcisme: ${video.title}`,
        tags: ['stoicisme', 'philosophie', 'sagesse', 'développement personnel']
      });

      alert('🎉 Vidéo uploadée sur YouTube avec succès !');
      window.open(response.data.youtube_url, '_blank');
      await loadVideos();
    } catch (error) {
      console.error('Error uploading to YouTube:', error);
      alert('Erreur lors de l\'upload: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(null);
    }
  };

  const handleUpdateMetadata = async (video, metadata) => {
    try {
      await youtubeApi.updateVideoMetadata(video.youtube_video_id, metadata);
      alert('✅ Métadonnées mises à jour sur YouTube !');
      await loadVideos();
    } catch (error) {
      console.error('Error updating metadata:', error);
      throw error;
    }
  };

  const handleBulkSchedule = async (scheduleData) => {
    try {
      const response = await youtubeApi.scheduleBulk(
        scheduleData.startDate,
        scheduleData.videosPerDay,
        scheduleData.publishTimes
      );
      
      alert(`✅ ${response.data.scheduled_count} vidéo(s) planifiée(s) !`);
      await loadVideos();
    } catch (error) {
      console.error('Error scheduling:', error);
      throw error;
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = (video) => {
    if (video.youtube_video_id) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Uploadée
        </span>
      );
    }
    if (video.is_scheduled) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
          Planifiée
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        Prête
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

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Vidéos générées</h1>
        <p className="mt-2 text-sm text-gray-600">
          {videos.length} vidéo(s)
        </p>
      </div>

      {/* Filtres et tri */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filtres:</span>
          </div>
          
          <select
            value={statusFilter || ''}
            onChange={(e) => setStatusFilter(e.target.value || null)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Toutes</option>
            <option value="uploaded">Uploadées</option>
            <option value="scheduled">Planifiées</option>
            <option value="pending">En attente</option>
          </select>
          
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Trier par:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="created_at">Date de création</option>
              <option value="title">Titre</option>
              <option value="scheduled_publish_date">Date de publication</option>
            </select>
            
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="desc">Descendant</option>
              <option value="asc">Ascendant</option>
            </select>
          </div>
          
          <div className="ml-auto">
            <button
              onClick={() => setShowScheduler(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Planifier en masse
            </button>
          </div>
        </div>
      </div>

      {videos.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Video className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune vidéo</h3>
          <p className="mt-1 text-sm text-gray-500">
            Les vidéos générées apparaîtront ici
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {videos.map((video) => (
              <li key={video.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <Video className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {video.title}
                        </p>
                        <div className="mt-1 flex items-center space-x-2">
                          {getStatusBadge(video)}
                          <span className="text-xs text-gray-500">
                            {formatDuration(video.duration_seconds)}
                          </span>
                          <span className="text-xs text-gray-500">
                            {video.video_type === 'short' ? '9:16' : '16:9'}
                          </span>
                          {video.is_scheduled && video.scheduled_publish_date && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
                              <Calendar className="h-3 w-3 mr-1" />
                              {new Date(video.scheduled_publish_date).toLocaleString('fr-FR')}
                            </span>
                          )}
                          {video.youtube_url && (
                            <a
                              href={video.youtube_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="h-3 w-3 mr-1" />
                              Voir sur YouTube
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                    {video.youtube_video_id && (
                      <button
                        onClick={() => setEditingVideo(video)}
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        data-testid={`edit-metadata-${video.id}`}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Modifier
                      </button>
                    )}
                    {!video.youtube_video_id && (
                      <button
                        onClick={() => handleUploadToYouTube(video)}
                        disabled={uploading === video.id}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                        data-testid={`upload-video-${video.id}`}
                      >
                        {uploading === video.id ? (
                          <>
                            <Loader className="h-4 w-4 mr-1 animate-spin" />
                            Upload...
                          </>
                        ) : (
                          <>
                            <Youtube className="h-4 w-4 mr-1" />
                            Upload YouTube
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {editingVideo && (
        <EditVideoMetadataModal
          video={editingVideo}
          onClose={() => setEditingVideo(null)}
          onUpdate={(metadata) => handleUpdateMetadata(editingVideo, metadata)}
        />
      )}

      {showScheduler && (
        <BulkSchedulerModal
          videos={videos.filter(v => !v.youtube_video_id)}
          onClose={() => setShowScheduler(false)}
          onSchedule={handleBulkSchedule}
        />
      )}
    </div>
  );
}

export default VideosPage;
