import React, { useState } from 'react';
import { X, Loader, Calendar } from 'lucide-react';

function ScheduleVideoModal({ video, onClose, onSchedule }) {
  const [publishDate, setPublishDate] = useState('');
  const [publishTime, setPublishTime] = useState('09:00');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!publishDate) {
      alert('Veuillez sélectionner une date');
      return;
    }

    setLoading(true);

    try {
      // Combiner date et heure
      const datetime = `${publishDate}T${publishTime}:00`;
      await onSchedule(datetime);
      onClose();
    } catch (error) {
      console.error('Error scheduling:', error);
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed z-10 inset-0 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <Calendar className="h-6 w-6 text-blue-600 mr-2" />
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Planifier la publication
                </h3>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-700 font-medium mb-1">{video.title}</p>
              <p className="text-xs text-gray-500">Cette vidéo sera automatiquement publiée sur YouTube à la date et heure choisies.</p>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="publishDate" className="block text-sm font-medium text-gray-700">
                    Date de publication
                  </label>
                  <input
                    type="date"
                    id="publishDate"
                    value={publishDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setPublishDate(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="publishTime" className="block text-sm font-medium text-gray-700">
                    Heure de publication
                  </label>
                  <input
                    type="time"
                    id="publishTime"
                    value={publishTime}
                    onChange={(e) => setPublishTime(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>

                <div className="bg-blue-50 p-3 rounded-md">
                  <p className="text-sm text-blue-700">
                    📅 La vidéo sera publiée automatiquement le {publishDate ? new Date(publishDate).toLocaleDateString('fr-FR') : '...'} à {publishTime}
                  </p>
                </div>
              </div>

              <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader className="h-4 w-4 mr-2 animate-spin" />
                      Planification...
                    </>
                  ) : (
                    'Planifier'
                  )}
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ScheduleVideoModal;
