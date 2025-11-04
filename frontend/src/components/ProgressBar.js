import React from 'react';

function ProgressBar({ progress, status, currentStep }) {
  const getProgressColor = () => {
    if (progress === 100) return 'bg-green-600';
    if (progress >= 75) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-indigo-500';
    return 'bg-gray-400';
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-medium text-gray-700">
          {currentStep || 'En cours...'}
        </span>
        <span className="text-xs font-medium text-gray-600">
          {progress}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getProgressColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

export default ProgressBar;
