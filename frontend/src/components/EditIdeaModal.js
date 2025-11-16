import React, { useState } from 'react';
import { X, Save } from 'lucide-react';

function EditIdeaModal({ idea, onClose, onSave }) {
  const [title, setTitle] = useState(idea?.title || '');
  const [keywords, setKeywords] = useState(
    (idea?.keywords || []).join(', ')
  );
  const [videoType, setVideoType] = useState(idea?.video_type || 'short');
  const [durationSeconds, setDurationSeconds] = useState(idea?.duration_seconds || 30);
  const [sectionTitles, setSectionTitles] = useState(
    (idea?.section_titles || []).join('\n')
  );
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
      const sectionTitlesList = sectionTitles.split('\n').map(s => s.trim()).filter(s => s);
      
      await onSave({
        title: title.trim(),
        keywords: keywordList,
        video_type: videoType,
        duration_seconds: parseInt(durationSeconds),
        section_titles: sectionTitlesList
      });
      onClose();
    } catch (error) {
      console.error('Error saving:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">
            Éditer l'idée
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="p-6 space-y-4 overflow-y-auto flex-1">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Titre de la vidéo
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
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
                placeholder="stoïcisme, philosophie, sagesse"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  <option value="short">📱 Short (9:16)</option>
                  <option value="normal">📺 Normal (16:9)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Durée (secondes)
                </label>
                <input
                  type="number"
                  value={durationSeconds}
                  onChange={(e) => setDurationSeconds(e.target.value)}
                  min="10"
                  max="600"
                  className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Titres des sections (un par ligne)
              </label>
              <textarea
                value={sectionTitles}
                onChange={(e) => setSectionTitles(e.target.value)}
                rows={4}
                placeholder="Section 1: Introduction...
Section 2: Développement principal...
Section 3: Conclusion..."
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-2 text-sm text-gray-500">
                {sectionTitles.split('\n').filter(s => s.trim()).length} sections définies
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-800">
                💡 <strong>Note:</strong> Les modifications apportées à l'idée n'affecteront pas les scripts, audios ou vidéos déjà générés.
                Vous devrez régénérer ces éléments si nécessaire.
              </p>
            </div>
          </div>

          <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={saving || !title.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditIdeaModal;
