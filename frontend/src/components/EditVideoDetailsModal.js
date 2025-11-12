import React, { useState } from 'react';
import { X, Save } from 'lucide-react';

function EditVideoDetailsModal({ video, onClose, onSave }) {
  const [formData, setFormData] = useState({
    title: video.title || '',
    video_type: video.video_type || 'short',
    video_path: video.video_path || '',
    video_relative_path: video.video_relative_path || '',
    thumbnail_path: video.thumbnail_path || '',
    duration_seconds: video.duration_seconds || 0,
    youtube_video_id: video.youtube_video_id || '',
    youtube_url: video.youtube_url || '',
    scheduled_publish_date: video.scheduled_publish_date 
      ? new Date(video.scheduled_publish_date).toISOString().slice(0, 16) 
      : '',
    is_scheduled: video.is_scheduled || false
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Préparer les données pour l'API
      const updateData = {
        title: formData.title,
        video_type: formData.video_type,
        video_path: formData.video_path || null,
        video_relative_path: formData.video_relative_path || null,
        thumbnail_path: formData.thumbnail_path || null,
        duration_seconds: parseFloat(formData.duration_seconds),
        youtube_video_id: formData.youtube_video_id || null,
        youtube_url: formData.youtube_url || null,
        scheduled_publish_date: formData.scheduled_publish_date 
          ? new Date(formData.scheduled_publish_date).toISOString() 
          : null,
        is_scheduled: formData.is_scheduled
      };

      await onSave(updateData);
      onClose();
    } catch (error) {
      console.error('Error updating video:', error);
      alert('Erreur lors de la mise à jour: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">
            Modifier les détails de la vidéo
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Titre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Titre
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Type et Durée */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de vidéo
              </label>
              <select
                name="video_type"
                value={formData.video_type}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="short">Short (9:16)</option>
                <option value="normal">Normal (16:9)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Durée (secondes)
              </label>
              <input
                type="number"
                name="duration_seconds"
                value={formData.duration_seconds}
                onChange={handleChange}
                step="0.1"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Chemins */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chemin vidéo
              </label>
              <input
                type="text"
                name="video_path"
                value={formData.video_path}
                onChange={handleChange}
                placeholder="/app/ressources/videos/video.mp4"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chemin relatif vidéo
              </label>
              <input
                type="text"
                name="video_relative_path"
                value={formData.video_relative_path}
                onChange={handleChange}
                placeholder="videos/video.mp4"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chemin thumbnail
              </label>
              <input
                type="text"
                name="thumbnail_path"
                value={formData.thumbnail_path}
                onChange={handleChange}
                placeholder="/app/ressources/thumbnails/thumbnail.jpg"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
          </div>

          {/* Informations YouTube */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Informations YouTube</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ID vidéo YouTube
                </label>
                <input
                  type="text"
                  name="youtube_video_id"
                  value={formData.youtube_video_id}
                  onChange={handleChange}
                  placeholder="dQw4w9WgXcQ"
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL YouTube
                </label>
                <input
                  type="url"
                  name="youtube_url"
                  value={formData.youtube_url}
                  onChange={handleChange}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
            </div>
          </div>

          {/* Planification */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Planification</h4>
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_scheduled"
                  checked={formData.is_scheduled}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Vidéo planifiée
                </label>
              </div>
              {formData.is_scheduled && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date de publication
                  </label>
                  <input
                    type="datetime-local"
                    name="scheduled_publish_date"
                    value={formData.scheduled_publish_date}
                    onChange={handleChange}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Boutons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? (
                <>En cours...</>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Enregistrer
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditVideoDetailsModal;
