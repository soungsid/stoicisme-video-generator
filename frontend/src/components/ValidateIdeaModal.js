import React, { useState } from 'react';
import { X } from 'lucide-react';

function ValidateIdeaModal({ idea, onClose, onSubmit }) {
  const [videoType, setVideoType] = useState('short');
  const [duration, setDuration] = useState(30);
  const [keywords, setKeywords] = useState(idea.keywords.join(', '));

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const keywordsArray = keywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);
    
    onSubmit({
      video_type: videoType,
      duration_seconds: parseInt(duration),
      keywords: keywordsArray
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50" data-testid="validate-idea-modal">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Valider l'idée
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
            data-testid="close-modal"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Titre
            </label>
            <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
              {idea.title}
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de vidéo
            </label>
            <select
              value={videoType}
              onChange={(e) => setVideoType(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              data-testid="video-type-select"
            >
              <option value="short">Short (9:16) - Vertical</option>
              <option value="normal">Normal (16:9) - Horizontal</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Durée (secondes)
            </label>
            <input
              type="number"
              min="10"
              max="600"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              data-testid="duration-input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Recommandé: 30-60s pour shorts, 120-300s pour vidéos normales
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mots-clés SEO (séparés par des virgules)
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="stoicisme, philosophie, sagesse"
              data-testid="keywords-input"
            />
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              data-testid="submit-validation"
            >
              Valider
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ValidateIdeaModal;
