import { CheckSquare, Loader, Plus, Search, Square } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { ideasApi, pipelineApi } from '../api';
import ConfirmModal from '../components/ConfirmModal';
import GenerateIdeasModal from '../components/GenerateIdeasModal';
import IdeaCard from '../components/IdeaCard';
import Toast from '../components/Toast';

function IdeasPage() {
  const [ideas, setIdeas] = useState([]);
  const [filteredIdeas, setFilteredIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIdeas, setSelectedIdeas] = useState([]);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [confirmModal, setConfirmModal] = useState(null);
  const [toast, setToast] = useState(null);
  const [batchAction, setBatchAction] = useState('');
  const [processingBatch, setProcessingBatch] = useState(false);

  useEffect(() => {
    loadIdeas();
    const interval = setInterval(loadIdeas, 6000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterIdeas();
  }, [searchQuery, ideas]);

  const loadIdeas = async () => {
    try {
      if (!loading) setLoading(true);
      const response = await ideasApi.getAllIdeas();
      setIdeas(response.data);
    } catch (error) {
      console.error('Error loading ideas:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterIdeas = () => {
    if (!searchQuery.trim()) {
      setFilteredIdeas(ideas);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = ideas.filter(idea =>
      idea.title.toLowerCase().includes(query) ||
      idea.keywords.some(k => k.toLowerCase().includes(query)) ||
      idea.status.toLowerCase().includes(query)
    );
    setFilteredIdeas(filtered);
  };

  const handleGenerateIdeas = async (data) => {
    try {
      setGenerating(true);

      if (data.type === 'auto') {
        // Option 1: Génération automatique
        await ideasApi.generateIdeas({
          count: data.count,
          video_type: data.videoType,
          duration_seconds: data.duration,
          sections_count: data.sectionsCount
        });
        setToast({ type: 'success', message: `${data.count} idées générées avec succès !` });
      } else if (data.type === 'keywords') {
        // Option 2: Avec mots-clés
        await ideasApi.generateIdeas({
          count: data.count,
          keywords: data.keywords,
          video_type: data.videoType,
          duration_seconds: data.duration,
          sections_count: data.sectionsCount
        });
        setToast({ type: 'success', message: `${data.count} idées générées avec les mots-clés !` });
      } else if (data.type === 'custom') {
        // Option 3: Script custom
        await ideasApi.createWithCustomScript({
          script_text: data.script,
          custom_title: data.customTitle,
          keywords: data.keywords,
          video_type: data.videoType,
          duration_seconds: data.duration
        });
        setToast({ type: 'success', message: 'Idée créée avec votre script !' });
      }

      await loadIdeas();
    } catch (error) {
      console.error('Error generating ideas:', error);
      setToast({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Erreur lors de la génération' 
      });
    } finally {
      setGenerating(false);
    }
  };


  const handleDeleteIdea = (ideaId) => {
    setConfirmModal({
      title: 'Supprimer cette idée ?',
      message: 'Cette action est irréversible.',
      danger: true,
      onConfirm: async () => {
        try {
          await ideasApi.deleteIdea(ideaId);
          setToast({ type: 'success', message: 'Idée supprimée' });
          await loadIdeas();
        } catch (error) {
          console.error('Error deleting:', error);
          setToast({ type: 'error', message: 'Erreur lors de la suppression' });
        }
        setConfirmModal(null);
      },
      onCancel: () => setConfirmModal(null)
    });
  };

  const handleStartPipeline = async (ideaId, startFrom = 'script') => {
    try {
      await pipelineApi.startPipeline(ideaId, startFrom);
      setToast({ type: 'info', message: 'Pipeline démarré' });
      await loadIdeas();
    } catch (error) {
      console.error('Error starting pipeline:', error);
      setToast({ type: 'error', message: error.response?.data?.detail || 'Erreur pipeline' });
    }
  };

  const handleBulkStart = () => {
    if (selectedIdeas.length === 0) {
      setToast({ type: 'warning', message: 'Sélectionnez au moins une idée' });
      return;
    }

    setConfirmModal({
      title: `Lancer ${selectedIdeas.length} pipeline(s) ?`,
      message: 'Les vidéos seront générées les unes après les autres.',
      onConfirm: async () => {
        for (const ideaId of selectedIdeas) {
          await handleStartPipeline(ideaId);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        setSelectedIdeas([]);
        setToast({ type: 'success', message: `${selectedIdeas.length} pipelines lancés` });
        setConfirmModal(null);
      },
      onCancel: () => setConfirmModal(null)
    });
  };

  const toggleSelectIdea = (ideaId) => {
    setSelectedIdeas(prev =>
      prev.includes(ideaId) ? prev.filter(id => id !== ideaId) : [...prev, ideaId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIdeas.length === filteredIdeas.length) {
      setSelectedIdeas([]);
    } else {
      setSelectedIdeas(filteredIdeas.map(idea => idea.id));
    }
  };

  const handleBatchAction = async () => {
    if (!batchAction || selectedIdeas.length === 0) {
      setToast({ type: 'error', message: 'Sélectionnez une action et au moins une idée' });
      return;
    }

    const actionLabels = {
      'delete': 'Supprimer',
      'generate': 'Lancer la génération'
    };

    setConfirmModal({
      title: `${actionLabels[batchAction]} ${selectedIdeas.length} idée(s) ?`,
      message: `Cette action sera appliquée à toutes les idées sélectionnées.`,
      onConfirm: async () => {
        try {
          setProcessingBatch(true);
          const response = await ideasApi.batchAction(selectedIdeas, batchAction);
          
          const successCount = response.data.results.success.length;
          const failedCount = response.data.results.failed.length;
          
          let message = `${successCount} idée(s) traitée(s) avec succès`;
          if (failedCount > 0) {
            message += `, ${failedCount} échec(s)`;
          }
          
          setToast({ type: successCount > 0 ? 'success' : 'error', message });
          setSelectedIdeas([]);
          setBatchAction('');
          await loadIdeas();
        } catch (error) {
          setToast({ type: 'error', message: 'Erreur: ' + (error.response?.data?.detail || error.message) });
        } finally {
          setProcessingBatch(false);
          setConfirmModal(null);
        }
      },
      onCancel: () => setConfirmModal(null)
    });
  };


  if (loading && ideas.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  const allSelected = selectedIdeas.length === filteredIdeas.length && filteredIdeas.length > 0;

  return (
    <div>
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Idées de vidéos</h1>
            <p className="mt-1 text-sm text-gray-600">
              {ideas.length} idée{ideas.length > 1 ? 's' : ''} • {filteredIdeas.length} affichée{filteredIdeas.length > 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={() => setShowGenerateModal(true)}
            disabled={generating}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? <Loader className="h-5 w-5 mr-2 animate-spin" /> : <Plus className="h-5 w-5 mr-2" />}
            Générer
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {selectedIdeas.length > 0 && (
            <div className="flex items-center gap-2">
              <select
                value={batchAction}
                onChange={(e) => setBatchAction(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Sélectionner une action...</option>
                <option value="generate">Lancer la génération</option>
                <option value="delete">Supprimer</option>
              </select>
              <button
                onClick={handleBatchAction}
                disabled={!batchAction || processingBatch}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {processingBatch ? (
                  <>
                    <Loader className="h-4 w-4 mr-2 animate-spin" />
                    Traitement...
                  </>
                ) : (
                  <>
                    Exécuter ({selectedIdeas.length})
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {filteredIdeas.length > 0 && (
          <div className="mt-3 flex items-center">
            <button onClick={toggleSelectAll} className="flex items-center text-sm text-gray-600 hover:text-gray-900">
              {allSelected ? <CheckSquare className="h-4 w-4 mr-2" /> : <Square className="h-4 w-4 mr-2" />}
              {allSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
            </button>
            {selectedIdeas.length > 0 && (
              <span className="ml-3 text-sm text-gray-600">
                {selectedIdeas.length} sélectionnée{selectedIdeas.length > 1 ? 's' : ''}
              </span>
            )}
          </div>
        )}
      </div>

      {filteredIdeas.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Search className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchQuery ? 'Aucun résultat' : 'Aucune idée'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery ? 'Essayez un autre terme' : 'Générez des idées pour commencer'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredIdeas.map((idea) => (
            <IdeaCard
              key={idea.id}
              idea={idea}
              selected={selectedIdeas.includes(idea.id)}
              onToggleSelect={() => toggleSelectIdea(idea.id)}
              onDelete={() => handleDeleteIdea(idea.id)}
              onStartPipeline={(startFrom) => handleStartPipeline(idea.id, startFrom)}
            />
          ))}
        </div>
      )}

      {showGenerateModal && (
        <GenerateIdeasModal
          onClose={() => setShowGenerateModal(false)}
          onSubmit={handleGenerateIdeas}
        />
      )}

      {confirmModal && (
        <ConfirmModal
          title={confirmModal.title}
          message={confirmModal.message}
          danger={confirmModal.danger}
          onConfirm={confirmModal.onConfirm}
          onCancel={confirmModal.onCancel}
        />
      )}

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

export default IdeasPage;
