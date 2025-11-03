import React from 'react';
import { CheckCircle, XCircle, Trash2, Play, Loader } from 'lucide-react';

function IdeaCard({ idea, onValidate, onReject, onDelete, onGeneratePipeline, processing }) {
  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { label: 'En attente', className: 'bg-yellow-100 text-yellow-800' },
      validated: { label: 'Validée', className: 'bg-blue-100 text-blue-800' },
      script_generated: { label: 'Script généré', className: 'bg-indigo-100 text-indigo-800' },
      audio_generated: { label: 'Audio généré', className: 'bg-purple-100 text-purple-800' },
      video_generated: { label: 'Vidéo générée', className: 'bg-green-100 text-green-800' },
      uploaded: { label: 'Uploadée', className: 'bg-green-600 text-white' },
      rejected: { label: 'Rejetée', className: 'bg-red-100 text-red-800' },
    };
    
    const status_info = statusMap[status] || statusMap.pending;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status_info.className}`}>
        {status_info.label}
      </span>
    );
  };

  const isPending = idea.status === 'pending';
  const isValidated = idea.status === 'validated';

  return (
    <div className="bg-white shadow rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow" data-testid={`idea-card-${idea.id}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            {getStatusBadge(idea.status)}
            {idea.video_type && (
              <span className="text-xs text-gray-500">
                {idea.video_type === 'short' ? '📱 Short (9:16)' : '📺 Normal (16:9)'}
              </span>
            )}
            {idea.duration_seconds && (
              <span className="text-xs text-gray-500">
                ⏱️ {idea.duration_seconds}s
              </span>
            )}
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {idea.title}
          </h3>
          
          {idea.keywords && idea.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {idea.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                >
                  #{keyword}
                </span>
              ))}
            </div>
          )}
        </div>
        
        <div className="ml-4 flex flex-col space-y-2">
          {isPending && (
            <>
              <button
                onClick={onValidate}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                data-testid={`validate-idea-${idea.id}`}
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Valider
              </button>
              <button
                onClick={onReject}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                data-testid={`reject-idea-${idea.id}`}
              >
                <XCircle className="h-4 w-4 mr-1" />
                Rejeter
              </button>
            </>
          )}
          
          {isValidated && onGeneratePipeline && (
            <button
              onClick={onGeneratePipeline}
              disabled={processing}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              data-testid={`generate-pipeline-${idea.id}`}
            >
              {processing ? (
                <>
                  <Loader className="h-4 w-4 mr-1 animate-spin" />
                  Génération...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-1" />
                  Générer
                </>
              )}
            </button>
          )}
          
          {onDelete && (
            <button
              onClick={onDelete}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-red-600 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              data-testid={`delete-idea-${idea.id}`}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Supprimer
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default IdeaCard;
