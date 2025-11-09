import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Ideas API
export const ideasApi = {
  generateIdeas: (count = 5, keywords = null) => 
    api.post('/api/ideas/generate', { count, keywords }),
  createWithCustomScript: (data) => 
    api.post('/api/ideas/custom-script', data),
  getAllIdeas: () => api.get('/api/ideas/'),
  getIdea: (id) => api.get(`/api/ideas/${id}`),
  validateIdea: (id, data) => api.patch(`/api/ideas/${id}/validate`, data),
  rejectIdea: (id) => api.patch(`/api/ideas/${id}/reject`),
  deleteIdea: (id) => api.delete(`/api/ideas/${id}`),
};

// Scripts API
export const scriptsApi = {
  generateScript: (ideaId, durationSeconds) => 
    api.post('/api/scripts/generate', { idea_id: ideaId, duration_seconds: durationSeconds }),
  getScript: (id) => api.get(`/api/scripts/${id}`),
  getScriptByIdea: (ideaId) => api.get(`/api/scripts/by-idea/${ideaId}`),
  updateScript: (scriptId, data) => 
    api.patch(`/api/scripts/${scriptId}`, null, { params: data }),
  adaptScript: (scriptId) => api.post(`/api/scripts/${scriptId}/adapt`),
};

// Audio API
export const audioApi = {
  generateAudio: (scriptId) => api.post(`/api/audio/generate/${scriptId}`),
  getAudioByScript: (scriptId) => api.get(`/api/audio/by-script/${scriptId}`),
};

// Videos API
export const videosApi = {
  generateVideo: (scriptId) => api.post(`/api/videos/generate/${scriptId}`),
  getVideo: (id) => api.get(`/api/videos/${id}`),
  getVideoByIdea: (ideaId) => api.get(`/api/videos/by-idea/${ideaId}`),
  listVideos: () => api.get('/api/videos/'),
};

// YouTube API
export const youtubeApi = {
  getAuthUrl: () => api.get('/api/youtube/auth/url'),
  getConfig: () => api.get('/api/youtube/config'),
  getChannelInfo: () => api.get('/api/youtube/channel-info'),
  uploadVideo: (videoId, data) => api.post(`/api/youtube/upload/${videoId}`, data),
  updateVideoMetadata: (youtubeVideoId, data) => api.patch(`/api/youtube/update/${youtubeVideoId}`, null, { params: data }),
};

// Config API
export const configApi = {
  getElevenLabsConfig: () => api.get('/api/config/elevenlabs'),
  getElevenLabsStats: () => api.get('/api/config/elevenlabs/stats'),
  getLLMConfig: () => api.get('/api/config/llm'),
  getYouTubeStats: () => api.get('/api/config/youtube/stats'),
  updateYouTubeConfig: (credentials) => api.post('/api/config/youtube', credentials),
};

// Pipeline API
export const pipelineApi = {
  startPipeline: (ideaId, startFrom = 'script') => 
    api.post(`/api/pipeline/generate/${ideaId}?start_from=${startFrom}`),
  getPipelineStatus: (ideaId) => api.get(`/api/pipeline/status/${ideaId}`),
};

// Queue API
export const queueApi = {
  getStats: () => api.get('/api/queue/stats'),
  getJobStatus: (ideaId) => api.get(`/api/queue/status/${ideaId}`),
  cancelJob: (ideaId) => api.post(`/api/queue/cancel/${ideaId}`),
};

export default api;
