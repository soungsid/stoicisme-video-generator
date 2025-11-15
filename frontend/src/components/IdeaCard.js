import { AlertCircle, CheckCircle, CheckSquare, Clock, FileText, Loader, Play, Square, Trash2, X, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { queueApi } from '../api';
import ProgressBar from './ProgressBar';

function IdeaCard({ idea, selected, onToggleSelect, onValidate, onReject, onDelete, onStartPipeline }) {
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
      pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-800', progress: 0 },
      validated: { label: 'Validée', color: 'bg-blue-100 text-blue-800', progress: 5 },
      queued: { label: 'En attente (queue)', color: 'bg-orange-100 text-orange-800', progress: 5 },
      processing: { label: 'En traitement', color: 'bg-blue-500 text-white', progress: 10 },
      script_generating: { label: 'Génération script...', color: 'bg-indigo-100 text-indigo-800', progress: 15 },
      script_generated: { label: 'Script prêt', color: 'bg-indigo-200 text-indigo-900', progress: 25 },
      script_adapting: { label: 'Adaptation...', color: 'bg-purple-100 text-purple-800', progress: 40 },
      script_adapted: { label: 'Script adapté', color: 'bg-purple-200 text-purple-900', progress: 50 },
      audio_generating: { label: 'Audio en cours...', color: 'bg-pink-100 text-pink-800', progress: 65 },
      audio_generated: { label: 'Audio prêt', color: 'bg-pink-200 text-pink-900', progress: 75 },
      video_generating: { label: 'Vidéo en cours...', color: 'bg-green-100 text-green-800', progress: 90 },
      video_generated: { label: 'Vidéo prête', color: 'bg-green-600 text-white', progress: 100 },
      uploaded: { label: 'Uploadée', color: 'bg-green-700 text-white', progress: 100 },
      rejected: { label: 'Rejetée', color: 'bg-red-100 text-red-800', progress: 0 },
      error: { label: 'Erreur', color: 'bg-red-600 text-white', progress: 0 },
    };
    return statusMap[status] || statusMap.pending;
  };

  const getNextStep = (status, lastSuccessful) => {
    if (status === 'error' && lastSuccessful) {
      // Déterminer l'étape suivante basée sur la dernière étape réussie
      const stepMap = {
        'script_generated': { label: 'Continuer (Adapter)', step: 'adapt' },
        'script_adapted': { label: 'Continuer (Audio)', step: 'audio' },
        'audio_generated': { label: 'Continuer (Vidéo)', step: 'video' },
      };
      return stepMap[lastSuccessful] || { label: 'Continuer', step: 'script' };
    }
    
    const stepMap = {
      validated: { label: 'Générer', step: 'script' },
      script_generated: { label: 'Adapter', step: 'adapt' },
      script_adapted: { label: 'Audio', step: 'audio' },
      audio_generated: { label: 'Vidéo', step: 'video' },
      error: { label: 'Recommencer', step: 'script' },
    };
    return stepMap[status];
  };

  const statusInfo = getStatusInfo(idea.status);
  const nextStep = getNextStep(idea.status, idea.last_successful_step);
  const isPending = idea.status === 'pending';
  const isQueued = idea.status === 'queued';
  const isError = idea.status === 'error';
  const isProcessing = ['processing', 'script_generating', 'script_adapting', 'audio_generating', 'video_generating'].includes(idea.status);
  const canResume = ['validated', 'script_generated', 'script_adapted', 'audio_generated', 'error'].includes(idea.status);
  const hasScript = ['script_generated', 'script_adapted', 'script_adapting', 'audio_generated', 'audio_generating', 'video_generated', 'video_generating', 'uploaded'].includes(idea.status);

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

          {/* Progress Bar */}
          {idea.progress_percentage > 0 && (
            <div className="mt-3">
              <ProgressBar 
                progress={idea.progress_percentage} 
                status={idea.status}
                currentStep={idea.current_step}
              />
            </div>
          )}

          {/* Error Message */}
          {isError && idea.error_message && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  {idea.last_successful_step && (
                    <p className="text-sm font-medium text-green-700 mb-2">
                      ✅ Dernière étape réussie: {idea.last_successful_step}
                    </p>
                  )}
                  <p className="text-sm text-red-800">{idea.error_message}</p>
                </div>
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
            <>
              <button
                onClick={onValidate}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Valider
              </button>
              <button
                onClick={onReject}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <XCircle className="h-4 w-4 mr-1" />
                Rejeter
              </button>
            </>
          )}
          
          {/* En cas d'erreur: 2 boutons */}
          {isError && idea.last_successful_step && nextStep && (
            <>
              <button
                onClick={() => onStartPipeline(nextStep.step)}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
              >
                <Play className="h-4 w-4 mr-1" />
                {nextStep.label}
              </button>
              <button
                onClick={() => onStartPipeline('script')}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Play className="h-4 w-4 mr-1" />
                Recommencer
              </button>
            </>
          )}
          
          {/* Pour les autres états qui peuvent reprendre */}
          {!isError && canResume && nextStep && (
            <button
              onClick={() => onStartPipeline(nextStep.step)}
              disabled={isProcessing}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {isProcessing ? (
                <Loader className="h-4 w-4 mr-1 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-1" />
              )}
              {nextStep.label}
            </button>
          )}
            <button
                onClick={() => onStartPipeline('video_generating')}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Play className="h-4 w-4 mr-1" />
                Regenerer Video
              </button>          
            <button
            onClick={onDelete}
            disabled={isProcessing || isQueued}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-red-600 bg-white hover:bg-red-50 disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            Supprimer
          </button>
        </div>
      </div>
    </div>
  );
}

export default IdeaCard;
