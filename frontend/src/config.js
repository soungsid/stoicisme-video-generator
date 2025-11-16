// Vérifie si la variable a été remplacée par envsubst
const isRuntimeConfigured = window.ENV?.BACKEND_URL && 
                           !window.ENV.BACKEND_URL.includes('${');

const backendUrl = isRuntimeConfigured 
  ? window.ENV.BACKEND_URL 
  : (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001');

  export const API_URL = backendUrl;
