import React, { useState } from 'react';
import { X, Sparkles, Tag, FileText } from 'lucide-react';

function GenerateIdeasModal({ onClose, onSubmit }) {
  const [activeTab, setActiveTab] = useState('auto');
  const [count, setCount] = useState(5);
  const [keywords, setKeywords] = useState('');
  const [customScript, setCustomScript] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [videoType, setVideoType] = useState('short');
  const [duration, setDuration] = useState(30);
  const [sectionsCount, setSectionsCount] = useState(3);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (activeTab === 'auto') {
        await onSubmit({ 
          type: 'auto', 
          count,
          videoType,
          duration,
          sectionsCount: videoType === 'normal' ? sectionsCount : null
        });
      } else if (activeTab === 'keywords') {
        const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
        await onSubmit({ 
          type: 'keywords', 
          count, 
          keywords: keywordList,
          videoType,
          duration,
          sectionsCount: videoType === 'normal' ? sectionsCount : null
        });
      } else if (activeTab === 'custom') {
        const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
        await onSubmit({ 
          type: 'custom', 
          script: customScript,
          customTitle: customTitle || null,
          keywords: keywordList,
          videoType,
          duration
        });
      }
      onClose();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">
            Générer des idées
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('auto')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'auto'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Sparkles className="inline h-4 w-4 mr-2" />
              Génération auto
            </button>
            <button
              onClick={() => setActiveTab('keywords')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'keywords'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Tag className="inline h-4 w-4 mr-2" />
              Avec mots-clés
            </button>
            <button
              onClick={() => setActiveTab('custom')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'custom'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FileText className="inline h-4 w-4 mr-2" />
              Script custom
            </button>
          </nav>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {activeTab === 'auto' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre d'idées à générer
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={count}
                  onChange={(e) => setCount(parseInt(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="mt-2 text-sm text-gray-500">
                  Le système génèrera automatiquement des titres et mots-clés optimisés.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de vidéo
                  </label>
                  <select
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
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
                    min="10"
                    max="600"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {videoType === 'normal' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de sections
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={sectionsCount}
                    onChange={(e) => setSectionsCount(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Pour les vidéos longues, le contenu sera structuré en sections thématiques.
                  </p>
                </div>
              )}
            </>
          )}

          {activeTab === 'keywords' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre d'idées
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={count}
                  onChange={(e) => setCount(parseInt(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mots-clés (séparés par des virgules)
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="stoicisme, Marc Aurèle, résilience"
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <p className="mt-2 text-sm text-gray-500">
                  Les idées générées seront basées sur ces mots-clés.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de vidéo
                  </label>
                  <select
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
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
                    min="10"
                    max="600"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {videoType === 'normal' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de sections
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={sectionsCount}
                    onChange={(e) => setSectionsCount(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Pour les vidéos longues, le contenu sera structuré en sections thématiques.
                  </p>
                </div>
              )}
            </>
          )}

          {activeTab === 'custom' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titre (optionnel)
                </label>
                <input
                  type="text"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  placeholder="Laissez vide pour générer automatiquement"
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="mt-2 text-sm text-gray-500">
                  Si non fourni, le système générera un titre à partir du script.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Votre script
                </label>
                <textarea
                  value={customScript}
                  onChange={(e) => setCustomScript(e.target.value)}
                  placeholder="Collez votre script ici..."
                  rows={8}
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  minLength={50}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de vidéo
                  </label>
                  <select
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
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
                    min="10"
                    max="600"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mots-clés (optionnel)
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="stoicisme, philosophie"
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </>
          )}

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
              className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Génération...' : 'Générer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default GenerateIdeasModal;
