import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Loader, Search, Play, CheckSquare, Square } from 'lucide-react';
import { ideasApi, pipelineApi } from '../api';
import IdeaCard from '../components/IdeaCard';
import ValidateIdeaModal from '../components/ValidateIdeaModal';

function IdeasPage() {
  const [ideas, setIdeas] = useState([]);
  const [filteredIdeas, setFilteredIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIdeas, setSelectedIdeas] = useState([]);
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [showValidateModal, setShowValidateModal] = useState(false);

  useEffect(() => {
    loadIdeas();
    const interval = setInterval(loadIdeas, 3000);
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

  const handleGenerateIdeas = async () => {
    try {
      setGenerating(true);
      const count = prompt('Combien d\'idées ?', '5');
      if (!count) return;

      await ideasApi.generateIdeas(parseInt(count));
      await loadIdeas();
    } catch (error) {
      console.error('Error generating ideas:', error);
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
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
      setShowValidateModal(false);
      await loadIdeas();
    } catch (error) {
      console.error('Error validating:', error);
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRejectIdea = async (ideaId) => {
    if (!window.confirm('Rejeter cette idée ?')) return;
    try {
      await ideasApi.rejectIdea(ideaId);
      await loadIdeas();
    } catch (error) {
      console.error('Error rejecting:', error);
    }
  };

  const handleDeleteIdea = async (ideaId) => {
    if (!window.confirm('Supprimer cette idée ?')) return;
    try {
      await ideasApi.deleteIdea(ideaId);
      await loadIdeas();
    } catch (error) {
      console.error('Error deleting:', error);
    }
  };

  const handleStartPipeline = async (ideaId, startFrom = 'script') => {
    try {
      await pipelineApi.startPipeline(ideaId, startFrom);
      await loadIdeas();
    } catch (error) {
      console.error('Error starting pipeline:', error);
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleBulkStart = async () => {
    if (selectedIdeas.length === 0) {
      alert('Sélectionnez au moins une idée');
      return;
    }

    if (!window.confirm(`Lancer ${selectedIdeas.length} pipeline(s) ?`)) return;

    for (const ideaId of selectedIdeas) {
      await handleStartPipeline(ideaId);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setSelectedIdeas([]);
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
            onClick={handleGenerateIdeas}
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
            <button
              onClick={handleBulkStart}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
            >
              <Play className="h-4 w-4 mr-2" />
              Générer ({selectedIdeas.length})
            </button>
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
              onValidate={() => handleValidateIdea(idea)}
              onReject={() => handleRejectIdea(idea.id)}
              onDelete={() => handleDeleteIdea(idea.id)}
              onStartPipeline={(startFrom) => handleStartPipeline(idea.id, startFrom)}
            />
          ))}
        </div>
      )}

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
