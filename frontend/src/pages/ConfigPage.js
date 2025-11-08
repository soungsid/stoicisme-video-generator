import React, { useState, useEffect } from 'react';
import { Mic, Brain, Youtube, CheckCircle, XCircle, Loader } from 'lucide-react';
import { configApi, youtubeApi } from '../api';

function ConfigPage() {
  const [elevenLabsConfig, setElevenLabsConfig] = useState(null);
  const [llmConfig, setLlmConfig] = useState(null);
  const [youtubeConfig, setYoutubeConfig] = useState(null);
  const [channelInfo, setChannelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingChannel, setLoadingChannel] = useState(false);

  useEffect(() => {
    loadConfigs();
    
    // Check for OAuth callback
    const params = new URLSearchParams(window.location.search);
    if (params.get('auth') === 'success') {
      alert('✅ Authentification YouTube réussie !');
      window.history.replaceState({}, document.title, window.location.pathname);
      loadConfigs();
    } else if (params.get('auth') === 'error') {
      alert('❌ Erreur lors de l\'authentification YouTube');
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const [elevenLabs, llm, youtube] = await Promise.all([
        configApi.getElevenLabsConfig(),
        configApi.getLLMConfig(),
        youtubeApi.getConfig()
      ]);
      
      setElevenLabsConfig(elevenLabs.data);
      setLlmConfig(llm.data);
      setYoutubeConfig(youtube.data);

      // Load channel info if authenticated
      if (youtube.data.is_authenticated) {
        loadChannelInfo();
      }
    } catch (error) {
      console.error('Error loading configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadChannelInfo = async () => {
    try {
      setLoadingChannel(true);
      const response = await youtubeApi.getChannelInfo();
      setChannelInfo(response.data);
    } catch (error) {
      console.error('Error loading channel info:', error);
    } finally {
      setLoadingChannel(false);
    }
  };

  const handleAuthenticateYouTube = async () => {
    try {
      const response = await youtubeApi.getAuthUrl();
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error('Error getting auth URL:', error);
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Configuration</h1>
        <p className="mt-2 text-sm text-gray-600">
          Gérez vos clés API et configurations
        </p>
      </div>

      <div className="space-y-6">
        {/* ElevenLabs Config */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Mic className="h-6 w-6 text-purple-500 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">ElevenLabs</h2>
          </div>
          
          {elevenLabsConfig && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Clés API configurées:</span>
                <span className="text-sm font-medium text-gray-900">
                  {elevenLabsConfig.total_keys} / 5
                </span>
              </div>
              
              <div className="space-y-2">
                {elevenLabsConfig.api_keys.map((key) => (
                  <div key={key.index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">Clé {key.index}</span>
                    {key.configured ? (
                      <div className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        <span className="text-xs font-mono">{key.key_preview}</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-gray-400">
                        <XCircle className="h-4 w-4 mr-1" />
                        <span className="text-xs">Non configurée</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Voix:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {elevenLabsConfig.voice_name} ({elevenLabsConfig.voice_id})
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* LLM Config */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Brain className="h-6 w-6 text-blue-500 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">LLM (Intelligence Artificielle)</h2>
          </div>
          
          {llmConfig && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Provider actif:</span>
                <span className="text-sm font-medium text-gray-900 uppercase">
                  {llmConfig.provider}
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">DeepSeek</span>
                  <div className="flex items-center">
                    {llmConfig.deepseek.configured ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-xs text-gray-600">{llmConfig.deepseek.model}</span>
                      </>
                    ) : (
                      <XCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">OpenAI</span>
                  <div className="flex items-center">
                    {llmConfig.openai.configured ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-xs text-gray-600">{llmConfig.openai.model}</span>
                      </>
                    ) : (
                      <XCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">Gemini</span>
                  <div className="flex items-center">
                    {llmConfig.gemini.configured ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-xs text-gray-600">{llmConfig.gemini.model}</span>
                      </>
                    ) : (
                      <XCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* YouTube Config */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Youtube className="h-6 w-6 text-red-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">YouTube</h2>
          </div>
          
          {youtubeConfig && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Statut d'authentification:</span>
                {youtubeConfig.is_authenticated ? (
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="h-5 w-5 mr-1" />
                    <span className="text-sm font-medium">Authentifié</span>
                  </div>
                ) : (
                  <div className="flex items-center text-gray-400">
                    <XCircle className="h-5 w-5 mr-1" />
                    <span className="text-sm font-medium">Non authentifié</span>
                  </div>
                )}
              </div>
              
              {!youtubeConfig.is_authenticated && (
                <div className="mt-4">
                  <p className="text-sm text-gray-600 mb-3">
                    Vous devez authentifier votre compte YouTube pour pouvoir uploader des vidéos.
                  </p>
                  <button
                    onClick={handleAuthenticateYouTube}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    data-testid="authenticate-youtube-btn"
                  >
                    <Youtube className="h-4 w-4 mr-2" />
                    Authentifier avec YouTube
                  </button>
                </div>
              )}
              
              {youtubeConfig.is_authenticated && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-800">
                    ✅ Votre compte YouTube est connecté. Vous pouvez maintenant uploader des vidéos.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-sm font-medium text-blue-900 mb-2">💡 Configuration des clés API</h3>
          <p className="text-sm text-blue-800">
            Pour configurer ou modifier les clés API, éditez le fichier <code className="bg-blue-100 px-1 py-0.5 rounded">.env</code> du backend.
          </p>
          <ul className="mt-2 text-sm text-blue-800 list-disc list-inside space-y-1">
            <li>ElevenLabs: ELEVENLABS_API_KEY1 à ELEVENLABS_API_KEY5</li>
            <li>DeepSeek: DEEPSEEK_API_KEY</li>
            <li>YouTube: YOUTUBE_CLIENT_ID et YOUTUBE_CLIENT_SECRET</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ConfigPage;
