import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader, Video as VideoIcon, Clock, Edit, FileText, Tag } from 'lucide-react';
import { scriptsApi, videosApi, ideasApi } from '../api';
import EditScriptModal from '../components/EditScriptModal';
import Toast from '../components/Toast';

function ScriptDetailPage() {
  const { ideaId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [script, setScript] = useState(null);
  const [idea, setIdea] = useState(null);
  const [video, setVideo] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    loadData();
  }, [ideaId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Charger l'idée
      const ideaRes = await ideasApi.getIdea(ideaId);
      setIdea(ideaRes.data);
      
      // Charger le script
      try {
        const scriptRes = await scriptsApi.getScriptByIdea(ideaId);
        setScript(scriptRes.data);
      } catch (err) {
        console.log('No script yet');
      }
      
      // Essayer de charger la vidéo
      try {
        const videoRes = await videosApi.getVideoByIdea(ideaId);
        setVideo(videoRes.data);
      } catch (err) {
        console.log('No video yet');
      }
    } catch (error) {
      console.error('Error loading:', error);
      setToast({ type: 'error', message: 'Erreur lors du chargement' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveScript = async (data) => {
    try {
      await scriptsApi.updateScript(script.id, data);
      setToast({ type: 'success', message: 'Script mis à jour avec succès' });
      await loadData();
    } catch (error) {
      console.error('Error updating script:', error);
      setToast({ type: 'error', message: 'Erreur lors de la mise à jour' });
      throw error;
    }
  };

  const formatTimestamp = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const cleanText = (text) => {
    // Supprimer les marqueurs ElevenLabs pour l'affichage
    return text.replace(/\[.*?\]/g, '').replace(/\s+/g, ' ').trim();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Idée non trouvée</p>
        <button
          onClick={() => navigate('/ideas')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          Retour aux idées
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Retour
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{idea.title}</h1>
            {idea.keywords && idea.keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {idea.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {keyword}
                  </span>
                ))}
              </div>
            )}
          </div>
          {script && (
            <button
              onClick={() => setShowEditModal(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Edit className="h-4 w-4 mr-2" />
              Éditer
            </button>
          )}
        </div>
      </div>

      {!script ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <FileText className="mx-auto h-12 w-12 text-yellow-600 mb-3" />
          <p className="text-sm text-yellow-800">
            Le script n'a pas encore été généré pour cette idée.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Original Script */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Script Original</h2>
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap text-gray-700">{script.original_script}</p>
              </div>
            </div>

            {/* Adapted Script */}
            {script.elevenlabs_adapted_script && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Script Adapté ElevenLabs</h2>
                <div className="prose max-w-none">
                  <p className="whitespace-pre-wrap text-gray-700">{script.elevenlabs_adapted_script}</p>
                </div>
              </div>
            )}

            {/* Phrases with Timestamps */}
            {script.audio_phrases && script.audio_phrases.length > 0 && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Phrases avec Timestamps ({script.audio_phrases.length})
                </h2>
                <div className="space-y-3">
                  {script.audio_phrases.map((phrase, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-blue-500 pl-4 py-2 bg-gray-50 rounded-r"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-500">
                          Phrase {phrase.phrase_index + 1}
                        </span>
                        <div className="flex items-center text-xs text-gray-500">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatTimestamp(phrase.start_time_ms)} - {formatTimestamp(phrase.end_time_ms)}
                          <span className="ml-2 text-gray-400">({(phrase.duration_ms / 1000).toFixed(1)}s)</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-800">{cleanText(phrase.phrase_text)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Video Player */}
            {video && video.video_path && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <VideoIcon className="h-5 w-5 mr-2" />
                  Vidéo
                </h2>
                <video
                  controls
                  className="w-full rounded-lg"
                  src={video.video_path}
                >
                  Votre navigateur ne supporte pas la vidéo.
                </video>
                <div className="mt-3 text-sm text-gray-600">
                  <p>Durée: {video.duration_seconds.toFixed(1)}s</p>
                  <p>Type: {video.video_type === 'short' ? 'Short (9:16)' : 'Normal (16:9)'}</p>
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistiques</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Statut</span>
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {idea.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Type</span>
                  <span className="text-sm font-medium text-gray-900">
                    {idea.video_type === 'short' ? 'Short' : 'Normal'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Durée cible</span>
                  <span className="text-sm font-medium text-gray-900">
                    {idea.duration_seconds}s
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Phrases totales</span>
                  <span className="text-sm font-medium text-gray-900">
                    {script.phrases ? script.phrases.length : 0}
                  </span>
                </div>
                {script.audio_phrases && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Phrases audio</span>
                      <span className="text-sm font-medium text-gray-900">
                        {script.audio_phrases.length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Durée totale</span>
                      <span className="text-sm font-medium text-gray-900">
                        {formatTimestamp(
                          script.audio_phrases[script.audio_phrases.length - 1]?.end_time_ms || 0
                        )}
                      </span>
                    </div>
                  </>
                )}
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Créé le</span>
                  <span className="text-sm font-medium text-gray-900">
                    {new Date(script.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <EditScriptModal
          script={script}
          idea={idea}
          onClose={() => setShowEditModal(false)}
          onSave={handleSaveScript}
        />
      )}

      {/* Toast */}
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

export default ScriptDetailPage;
