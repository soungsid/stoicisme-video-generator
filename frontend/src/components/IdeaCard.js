import { AlertCircle, CheckCircle, CheckSquare, Clock, FileText, Play, Square, Trash2, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { queueApi } from '../api';

const StatusIndicator = ({ status }) => {
  const steps = ['Script', 'Audio', 'Vidéo'];
  const statusOrder = ['script_generated', 'audio_generated', 'video_generated'];
  
  // Déterminer l'index actif basé sur le statut
  let activeIndex = statusOrder.indexOf(status);
  
  // Si le statut est 'queued', on est à l'étape 0 (script)
  if (status === 'queued') activeIndex = 0;
  
  // Si le statut n'est pas dans l'ordre, on utilise -1 (aucune étape active)
  if (activeIndex === -1 && status !== 'queued') activeIndex = -1;

  return (
    <div className="flex items-center space-x-4">
      {steps.map((step, index) => {
        // Une étape est complétée si son index est inférieur à l'index actif
        const isCompleted = activeIndex > index;
        // L'étape actuelle est celle qui correspond à l'index actif
        const isCurrent = activeIndex === index;
        const isError = status === 'error';

        return (
          <div key={step} className="flex items-center">
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center ${
                isCompleted ? 'bg-green-500' : 
                isError ? 'bg-red-500' : 
                isCurrent ? 'bg-blue-500' : 
                'bg-gray-300'
              }`}
            >
              {isCompleted ? <CheckCircle className="w-4 h-4 text-white" /> : <span className="text-xs font-bold text-white">{index + 1}</span>}
            </div>
            <span className={`ml-2 text-sm ${isCompleted || isCurrent ? 'font-semibold text-gray-800' : 'text-gray-500'}`}>
              {step}
            </span>
          </div>
        );
      })}
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
      if (idea.status === 'queued' || idea.status === 'processing') {
        try {
          const response = await queueApi.getJobStatus(idea.id);
          setQueueInfo(response.data);
        } catch (error) {
          console.error('Error loading queue info:', error);
        }
      }
    };
    
    loadQueueInfo();
    
    // Rafraîchir toutes les 5 secondes si en queue ou processing
    const interval = setInterval(() => {
      if (idea.status === 'queued' || idea.status === 'processing') {
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
      pending: { label: 'Prêt à lancer', color: 'bg-yellow-100 text-yellow-800' },
      queued: { label: 'En attente', color: 'bg-orange-100 text-orange-800' },
      script_generated: { label: 'Script généré', color: 'bg-indigo-200 text-indigo-900' },
      audio_generated: { label: 'Audio généré', color: 'bg-pink-200 text-pink-900' },
      video_generated: { label: 'Terminé', color: 'bg-green-600 text-white' },
      error: { label: 'Erreur', color: 'bg-red-600 text-white' },
    };
    return statusMap[status] || statusMap.pending;
  };

  const statusInfo = getStatusInfo(idea.status);
  const isPending = idea.status === 'pending';
  const isQueued = idea.status === 'queued';
  const isError = idea.status === 'error';
  const isProcessing = idea.status === 'queued';
  const hasScript = !!idea.script_id ;

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
              <StatusIndicator status={idea.status} />
            </div>
          )}

          {/* Error Message */}
          {isError && idea.error_message && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{idea.error_message}</p>
              </div>
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
