import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'https://stoicisme-backend.manga-pics.com';

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
  batchAction: (ideaIds, action) => 
    api.post('/api/ideas/batch-action', null, { params: { idea_ids: ideaIds, action } }),
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
  getVideoDetails: (id) => api.get(`/api/videos/${id}/details`),
  getVideoByIdea: (ideaId) => api.get(`/api/videos/by-idea/${ideaId}`),
  listVideos: (statusFilter = null, sortBy = 'created_at', sortOrder = 'desc') => 
    api.get('/api/videos/', { params: { status_filter: statusFilter, sort_by: sortBy, sort_order: sortOrder } }),
};

// YouTube API
export const youtubeApi = {
  getAuthUrl: () => api.get('/api/youtube/auth/url'),
  getConfig: () => api.get('/api/youtube/config'),
  getChannelInfo: () => api.get('/api/youtube/channel-info'),
  disconnectYouTube: () => api.post('/api/youtube/disconnect'),
  uploadVideo: (videoId, data) => api.post(`/api/youtube/upload/${videoId}`, data),
  updateVideoMetadata: (youtubeVideoId, data) => api.patch(`/api/youtube/update/${youtubeVideoId}`, null, { params: data }),
  scheduleVideo: (videoId, publishDate) => api.post(`/api/youtube/schedule/${videoId}`, { publish_date: publishDate }),
  scheduleBulk: (startDate, videosPerDay, publishTimes) => 
    api.post('/api/youtube/schedule/bulk', {
      start_date: startDate,
      videos_per_day: videosPerDay,
      publish_times: publishTimes
    }),
  unscheduleVideo: (videoId) => api.delete(`/api/youtube/schedule/${videoId}`),
};

// Config API
export const configApi = {
  getElevenLabsConfig: () => api.get('/api/config/elevenlabs'),
  getElevenLabsKeysDetails: () => api.get('/api/config/elevenlabs/keys-details'),
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
