import React, { useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

function Toast({ type = 'info', message, onClose, autoDismiss = true, duration = 5000 }) {
  useEffect(() => {
    if (autoDismiss && onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoDismiss, duration, onClose]);
  const configs = {
    success: {
      icon: CheckCircle,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800',
      iconColor: 'text-green-600'
    },
    error: {
      icon: XCircle,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      iconColor: 'text-red-600'
    },
    warning: {
      icon: AlertCircle,
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      iconColor: 'text-yellow-600'
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      iconColor: 'text-blue-600'
    }
  };

  const config = configs[type];
  const Icon = config.icon;

  return (
    <div className={`fixed top-4 right-4 max-w-md w-full ${config.bgColor} border ${config.borderColor} rounded-lg shadow-lg p-4 animate-slide-in z-50`}>
      <div className="flex items-start">
        <Icon className={`h-5 w-5 ${config.iconColor} mr-3 flex-shrink-0 mt-0.5`} />
        <p className={`text-sm ${config.textColor} flex-1`}>{message}</p>
        {onClose && (
          <button
            onClick={onClose}
            className={`ml-3 ${config.textColor} hover:opacity-75`}
          >
            <XCircle className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}

export default Toast;
