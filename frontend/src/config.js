const backendUrl = window.ENV?.BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const API_URL = backendUrl;
