import React, { useState, useEffect } from 'react';
import { Plus, Loader, CheckCircle, XCircle, Trash2, Play } from 'lucide-react';
import { ideasApi, scriptsApi, audioApi, videosApi } from '../api';
import IdeaCard from '../components/IdeaCard';
import ValidateIdeaModal from '../components/ValidateIdeaModal';

function IdeasPage() {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [showValidateModal, setShowValidateModal] = useState(false);
  const [processingIdea, setProcessingIdea] = useState(null);

  useEffect(() => {
    loadIdeas();
  }, []);

  const loadIdeas = async () => {
    try {
      setLoading(true);
      const response = await ideasApi.getAllIdeas();
      setIdeas(response.data);
    } catch (error) {
      console.error('Error loading ideas:', error);
      alert('Erreur lors du chargement des idées');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateIdeas = async () => {
    try {
      setGenerating(true);
      const count = prompt('Combien d\'idées voulez-vous générer ?', '5');
      if (!count) return;

      const response = await ideasApi.generateIdeas(parseInt(count));
      alert(`${response.data.count} idées générées avec succès !`);
      await loadIdeas();
    } catch (error) {
      console.error('Error generating ideas:', error);
      alert('Erreur lors de la génération des idées: ' + (error.response?.data?.detail || error.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleValidateIdea = (idea) => {
    setSelectedIdea(idea);
    setShowValidateModal(true);
  };

  const handleValidateSubmit = async (validationData) => {
    try {
      await ideasApi.validateIdea(selectedIdea.id, validationData);
      alert('Idée validée avec succès !');
      setShowValidateModal(false);
      await loadIdeas();
    } catch (error) {
      console.error('Error validating idea:', error);
      alert('Erreur lors de la validation: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRejectIdea = async (ideaId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir rejeter cette idée ?')) return;
    
    try {
      await ideasApi.rejectIdea(ideaId);
      alert('Idée rejetée');
      await loadIdeas();
    } catch (error) {
      console.error('Error rejecting idea:', error);
      alert('Erreur lors du rejet de l\'idée');
    }
  };

  const handleDeleteIdea = async (ideaId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette idée ?')) return;
    
    try {
      await ideasApi.deleteIdea(ideaId);
      alert('Idée supprimée');
      await loadIdeas();
    } catch (error) {
      console.error('Error deleting idea:', error);
      alert('Erreur lors de la suppression');
    }
  };

  const handleGeneratePipeline = async (idea) => {
    if (!window.confirm('Lancer le pipeline complet de génération (script → audio → vidéo) ?')) return;

    try {
      setProcessingIdea(idea.id);

      // Étape 1: Générer le script
      alert('Génération du script...');
      const scriptResponse = await scriptsApi.generateScript(idea.id, idea.duration_seconds);
      const script = scriptResponse.data;

      // Étape 2: Adapter le script pour ElevenLabs
      alert('Adaptation du script pour ElevenLabs...');
      await scriptsApi.adaptScript(script.id);

      // Étape 3: Générer l'audio
      alert('Génération de l\'audio...');
      await audioApi.generateAudio(script.id);

      // Étape 4: Générer la vidéo
      alert('Génération de la vidéo...');
      await videosApi.generateVideo(script.id);

      alert('🎉 Pipeline terminé avec succès ! La vidéo est prête.');
      await loadIdeas();
    } catch (error) {
      console.error('Error in pipeline:', error);
      alert('Erreur dans le pipeline: ' + (error.response?.data?.detail || error.message));
    } finally {
      setProcessingIdea(null);
    }
  };

  const pendingIdeas = ideas.filter(i => i.status === 'pending');
  const validatedIdeas = ideas.filter(i => i.status !== 'pending' && i.status !== 'rejected');
  const rejectedIdeas = ideas.filter(i => i.status === 'rejected');

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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Idées de vidéos</h1>
            <p className="mt-2 text-sm text-gray-600">
              Générez et gérez vos idées de vidéos YouTube sur le stoïcisme
            </p>
          </div>
          <button
            onClick={handleGenerateIdeas}
            disabled={generating}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            data-testid="generate-ideas-btn"
          >
            {generating ? (
              <Loader className="h-5 w-5 mr-2 animate-spin" />
            ) : (
              <Plus className="h-5 w-5 mr-2" />
            )}
            Générer des idées
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
              <Loader className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">En attente</p>
              <p className="text-2xl font-semibold text-gray-900">{pendingIdeas.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <CheckCircle className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">En cours</p>
              <p className="text-2xl font-semibold text-gray-900">{validatedIdeas.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Rejetées</p>
              <p className="text-2xl font-semibold text-gray-900">{rejectedIdeas.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Ideas */}
      {pendingIdeas.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Idées en attente de validation</h2>
          <div className="grid grid-cols-1 gap-4">
            {pendingIdeas.map((idea) => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                onValidate={() => handleValidateIdea(idea)}
                onReject={() => handleRejectIdea(idea.id)}
                onDelete={() => handleDeleteIdea(idea.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Validated Ideas */}
      {validatedIdeas.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Idées validées</h2>
          <div className="grid grid-cols-1 gap-4">
            {validatedIdeas.map((idea) => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                onGeneratePipeline={() => handleGeneratePipeline(idea)}
                processing={processingIdea === idea.id}
              />
            ))}
          </div>
        </div>
      )}

      {/* No ideas */}
      {ideas.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Lightbulb className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune idée</h3>
          <p className="mt-1 text-sm text-gray-500">
            Commencez par générer des idées de vidéos
          </p>
        </div>
      )}

      {/* Validate Modal */}
      {showValidateModal && (
        <ValidateIdeaModal
          idea={selectedIdea}
          onClose={() => setShowValidateModal(false)}
          onSubmit={handleValidateSubmit}
        />
      )}
    </div>
  );
}

export default IdeasPage;
