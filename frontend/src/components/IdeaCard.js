import { AlertCircle, CheckCircle, CheckSquare, Clock, FileText, Play, Square, Trash2, X, Loader } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { queueApi } from '../api';

const StatusIndicator = ({ status, errorMessage }) => {
  // Tous les statuts dans l'ordre
  const allStatuses = [
    'pending',
    'queued', 
    'script_generating',
    'script_generated',
    'audio_generating',
    'audio_generated', 
    'video_generating',
    'video_generated'
  ];
  
  // Déterminer l'index du statut actuel
  const currentIndex = allStatuses.indexOf(status);
  const isError = status === 'error';
  
  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2 overflow-x-auto py-2">
        {allStatuses.map((stepStatus, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isGenerating = stepStatus.includes('generating');
          const isErrorStep = isError && index === currentIndex;

          return (
            <div key={stepStatus} className="flex items-center flex-shrink-0">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  isErrorStep ? 'bg-red-500' :
                  isCompleted ? 'bg-green-500' : 
                  isCurrent ? (isGenerating ? 'bg-blue-500' : 'bg-blue-300') : 
                  'bg-gray-300'
                }`}
              >
                {isErrorStep ? (
                  <AlertCircle className="w-4 h-4 text-white" />
                ) : isCompleted ? (
                  <CheckCircle className="w-4 h-4 text-white" />
                ) : isCurrent && isGenerating ? (
                  <Loader className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <span className="text-xs font-bold text-white">{index + 1}</span>
                )}
              </div>
              <span className={`ml-2 text-xs ${isCompleted || isCurrent ? 'font-semibold text-gray-800' : 'text-gray-500'}`}>
                {stepStatus.replace('_', ' ')}
              </span>
            </div>
          );
        })}
      </div>
      
      {/* Affichage du message d'erreur */}
      {isError && errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-start">
            <AlertCircle className="h-4 w-4 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{errorMessage}</p>
          </div>
        </div>
      )}
    </div>
  );
};

const ActionsDropdown = ({ onRegenerate }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button onClick={() => setIsOpen(!isOpen)} className="px-2 py-1 border rounded-md text-xs">...</button>
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
          <button onClick={() => { onRegenerate('script'); setIsOpen(false); }} className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Régénérer Script</button>
          <button onClick={() => { onRegenerate('audio'); setIsOpen(false); }} className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Régénérer Audio</button>
          <button onClick={() => { onRegenerate('video'); setIsOpen(false); }} className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Régénérer Vidéo</button>
        </div>
      )}
    </div>
  );
};


function IdeaCard({ idea, selected, onToggleSelect, onDelete, onStartPipeline }) {
  const navigate = useNavigate();
  const [queueInfo, setQueueInfo] = useState(null);
  
  // Charger les informations de queue
  useEffect(() => {
    const loadQueueInfo = async () => {
      if (idea.status === 'queued' || idea.status === 'processing' || 
          idea.status === 'script_generating' || idea.status === 'audio_generating' || idea.status === 'video_generating') {
        try {
          const response = await queueApi.getJobStatus(idea.id);
          setQueueInfo(response.data);
        } catch (error) {
          console.error('Error loading queue info:', error);
        }
      }
    };
    
    loadQueueInfo();
    
    // Rafraîchir toutes les 5 secondes si en queue ou en cours de génération
    const interval = setInterval(() => {
      if (idea.status === 'queued' || idea.status === 'processing' || 
          idea.status === 'script_generating' || idea.status === 'audio_generating' || idea.status === 'video_generating') {
        loadQueueInfo();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [idea.id, idea.status]);
  
  const handleCancelJob = async () => {
    if (!window.confirm('Annuler la génération ?')) return;
    
    try {
      await queueApi.cancelJob(idea.id);
      window.location.reload();
    } catch (error) {
      alert('Erreur lors de l\'annulation: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  const getStatusInfo = (status) => {
    const statusMap = {
      pending: { label: 'Prêt à lancer', color: 'bg-yellow-100 text-yellow-800', icon: null },
      queued: { label: 'En attente', color: 'bg-orange-100 text-orange-800', icon: <Clock className="h-3 w-3 mr-1" /> },
      script_generating: { label: 'Génération du script...', color: 'bg-blue-100 text-blue-800', icon: <Loader className="h-3 w-3 mr-1 animate-spin" /> },
      script_generated: { label: 'Script généré', color: 'bg-indigo-200 text-indigo-900', icon: null },
      audio_generating: { label: 'Génération audio...', color: 'bg-purple-100 text-purple-800', icon: <Loader className="h-3 w-3 mr-1 animate-spin" /> },
      audio_generated: { label: 'Audio généré', color: 'bg-pink-200 text-pink-900', icon: null },
      video_generating: { label: 'Génération vidéo...', color: 'bg-teal-100 text-teal-800', icon: <Loader className="h-3 w-3 mr-1 animate-spin" /> },
      video_generated: { label: 'Terminé', color: 'bg-green-600 text-white', icon: null },
      error: { label: 'Erreur', color: 'bg-red-600 text-white', icon: <AlertCircle className="h-3 w-3 mr-1" /> },
    };
    return statusMap[status] || statusMap.pending;
  };

  const statusInfo = getStatusInfo(idea.status);
  const isPending = idea.status === 'pending';
  const isQueued = idea.status === 'queued';
  const isError = idea.status === 'error';
  const isProcessing = idea.status === 'queued';
  const hasScript = !!idea.script_id;

  return (
    <div className="bg-white shadow rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <button
          onClick={onToggleSelect}
          className="mt-1 flex-shrink-0 text-gray-400 hover:text-blue-600 transition-colors"
        >
          {selected ? (
            <CheckSquare className="h-5 w-5 text-blue-600" />
          ) : (
            <Square className="h-5 w-5" />
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
                  {statusInfo.icon}
                  {statusInfo.label}
                </span>
                {isQueued && queueInfo && queueInfo.queue_position && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-200 text-orange-900">
                    <Clock className="h-3 w-3 mr-1" />
                    Position: {queueInfo.queue_position}
                  </span>
                )}
                {idea.video_type && (
                  <span className="text-xs text-gray-500">
                    {idea.video_type === 'short' ? '📱 Short' : '📺 Normal'} • {idea.duration_seconds}s
                  </span>
                )}
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {idea.title}
              </h3>
              
              {idea.keywords && idea.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {idea.keywords.slice(0, 5).map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                    >
                      #{keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Status Indicator */}
          {idea.status !== 'pending' && (
            <div className="mt-4">
              <StatusIndicator status={idea.status} errorMessage={idea.error_message} />
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          {hasScript && (
            <button
              onClick={() => navigate(`/script/${idea.id}`)}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <FileText className="h-4 w-4 mr-1" />
              Voir script
            </button>
          )}
          
          {isQueued && (
            <button
              onClick={handleCancelJob}
              className="inline-flex items-center px-3 py-1.5 border border-orange-300 text-xs font-medium rounded-md text-orange-700 bg-white hover:bg-orange-50"
            >
              <X className="h-4 w-4 mr-1" />
              Annuler
            </button>
          )}
          
          {isPending && (
            <button
              onClick={() => onStartPipeline('script')}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Play className="h-4 w-4 mr-1" />
              Lancer la génération
            </button>
          )}

          <div className="flex items-center gap-2">
            <button
              onClick={onDelete}
              disabled={isProcessing || isQueued}
              className="p-1.5 text-red-600 hover:bg-red-50 rounded-md disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            {!isPending && <ActionsDropdown onRegenerate={onStartPipeline} />}
          </div>
        </div>
      </div>
    </div>
  );
}

export default IdeaCard;
