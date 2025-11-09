import React, { useState } from 'react';
import { X, Loader, Calendar } from 'lucide-react';

function BulkSchedulerModal({ onClose, onSchedule }) {
  const [formData, setFormData] = useState({
    startDate: new Date().toISOString().split('T')[0],
    videosPerDay: 2,
    publishTimes: ['09:00', '18:00'],
  });
  const [loading, setLoading] = useState(false);
  const [newTime, setNewTime] = useState('12:00');

  const addPublishTime = () => {
    if (!formData.publishTimes.includes(newTime)) {
      setFormData({
        ...formData,
        publishTimes: [...formData.publishTimes, newTime].sort()
      });
    }
  };

  const removePublishTime = (time) => {
    setFormData({
      ...formData,
      publishTimes: formData.publishTimes.filter(t => t !== time)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.publishTimes.length === 0) {
      alert('Ajoutez au moins une heure de publication');
      return;
    }

    setLoading(true);

    try {
      await onSchedule(formData);
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

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <Calendar className="h-6 w-6 text-blue-600 mr-2" />
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Planification en masse
                </h3>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
                    Date de début
                  </label>
                  <input
                    type="date"
                    id="startDate"
                    value={formData.startDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="videosPerDay" className="block text-sm font-medium text-gray-700">
                    Nombre de vidéos par jour
                  </label>
                  <input
                    type="number"
                    id="videosPerDay"
                    min="1"
                    max="10"
                    value={formData.videosPerDay}
                    onChange={(e) => setFormData({ ...formData, videosPerDay: parseInt(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Heures de publication
                  </label>
                  
                  <div className="flex gap-2 mb-2">
                    <input
                      type="time"
                      value={newTime}
                      onChange={(e) => setNewTime(e.target.value)}
                      className="flex-1 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                    <button
                      type="button"
                      onClick={addPublishTime}
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                    >
                      Ajouter
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {formData.publishTimes.map(time => (
                      <div key={time} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                        {time}
                        <button
                          type="button"
                          onClick={() => removePublishTime(time)}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-blue-50 p-3 rounded-md">
                  <p className="text-sm text-blue-700">
                    📅 Les vidéos seront publiées automatiquement aux dates et heures configurées.
                    Le système les publiera dès que l'heure sera atteinte.
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

export default BulkSchedulerModal;
