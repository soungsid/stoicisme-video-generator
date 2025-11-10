import React, { useState, useEffect } from 'react';
import { Mic, Brain, Youtube, CheckCircle, XCircle, Loader } from 'lucide-react';
import { configApi, youtubeApi } from '../api';

function ConfigPage() {
  const [elevenLabsConfig, setElevenLabsConfig] = useState(null);
  const [elevenLabsKeys, setElevenLabsKeys] = useState(null);
  const [elevenLabsStats, setElevenLabsStats] = useState(null);
  const [llmConfig, setLlmConfig] = useState(null);
  const [youtubeConfig, setYoutubeConfig] = useState(null);
  const [youtubeStats, setYoutubeStats] = useState(null);
  const [channelInfo, setChannelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingChannel, setLoadingChannel] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);

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
      const [elevenLabs, elevenKeys, elevenStats, llm, youtube, ytStats] = await Promise.all([
        configApi.getElevenLabsConfig(),
        configApi.getElevenLabsKeysDetails(),
        configApi.getElevenLabsStats(),
        configApi.getLLMConfig(),
        youtubeApi.getConfig(),
        configApi.getYouTubeStats()
      ]);
      
      setElevenLabsConfig(elevenLabs.data);
      setElevenLabsKeys(elevenKeys.data);
      setElevenLabsStats(elevenStats.data);
      setLlmConfig(llm.data);
      setYoutubeConfig(youtube.data);
      setYoutubeStats(ytStats.data);

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

  const handleDisconnectYouTube = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir déconnecter ce compte YouTube ?')) {
      return;
    }
    
    try {
      setDisconnecting(true);
      await youtubeApi.disconnectYouTube();
      alert('✅ Compte YouTube déconnecté avec succès');
      await loadConfigs();
      setChannelInfo(null);
    } catch (error) {
      console.error('Error disconnecting YouTube:', error);
      alert('Erreur lors de la déconnexion: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDisconnecting(false);
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
              
              {elevenLabsStats && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">📊 Utilisation</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Scripts générés aujourd'hui:</span>
                      <span className="font-medium text-gray-900">{elevenLabsStats.scripts_generated_today}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Caractères estimés:</span>
                      <span className="font-medium text-gray-900">{elevenLabsStats.estimated_chars_today.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Rotation clés:</span>
                      <span className={`font-medium ${elevenLabsStats.rotation_status.enabled ? 'text-green-600' : 'text-gray-500'}`}>
                        {elevenLabsStats.rotation_status.enabled ? '✅ Activée' : '❌ Désactivée'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {elevenLabsKeys && elevenLabsKeys.keys && elevenLabsKeys.keys.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">🔑 Détails des Clés API</h4>
                  <div className="space-y-3">
                    {elevenLabsKeys.keys.map((keyInfo) => (
                      <div key={keyInfo.key_number} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-gray-700">Clé #{keyInfo.key_number}</span>
                          {keyInfo.status === 'error' ? (
                            <span className="text-xs px-2 py-0.5 bg-red-100 text-red-800 rounded">Erreur</span>
                          ) : (
                            <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded">{keyInfo.tier}</span>
                          )}
                        </div>
                        {keyInfo.error ? (
                          <p className="text-xs text-red-600">{keyInfo.error}</p>
                        ) : (
                          <>
                            <div className="space-y-1 text-xs">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Email:</span>
                                <span className="font-medium text-gray-900">{keyInfo.first_name} ({keyInfo.email})</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Clé:</span>
                                <span className="font-mono text-gray-700">{keyInfo.key}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Utilisés ce mois:</span>
                                <span className="font-medium text-gray-900">{keyInfo.character_count.toLocaleString()} car.</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Restants:</span>
                                <span className="font-medium text-green-600">{keyInfo.characters_remaining.toLocaleString()} car.</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Limite:</span>
                                <span className="font-medium text-gray-900">{keyInfo.character_limit.toLocaleString()} car.</span>
                              </div>
                            </div>
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${keyInfo.characters_remaining < keyInfo.character_limit * 0.2 ? 'bg-red-600' : 'bg-blue-600'}`}
                                  style={{ width: `${(keyInfo.character_count / keyInfo.character_limit) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
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

                    <button
                      onClick={handleAuthenticateYouTube}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      data-testid="authenticate-youtube-btn"
                    >
                      <Youtube className="h-4 w-4 mr-2" />
                      Se connecter avec un autre compte
                    </button>
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
                <div className="mt-4 space-y-4">
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-800">
                      ✅ Votre compte YouTube est connecté. Vous pouvez maintenant uploader des vidéos.
                    </p>
                  </div>

                  {loadingChannel ? (
                    <div className="flex items-center justify-center py-4">
                      <Loader className="h-5 w-5 animate-spin text-blue-500" />
                    </div>
                  ) : channelInfo ? (
                    <div className="space-y-3">
                      <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Informations de la chaîne</h4>
                        <div className="flex items-start space-x-4">
                          {channelInfo.thumbnail && (
                            <img 
                              src={channelInfo.thumbnail} 
                              alt={channelInfo.title}
                              className="w-16 h-16 rounded-full"
                            />
                          )}
                          <div className="flex-1 space-y-2">
                            <div>
                              <p className="text-sm font-medium text-gray-900">{channelInfo.title}</p>
                              {channelInfo.custom_url && (
                                <p className="text-xs text-gray-500">{channelInfo.custom_url}</p>
                              )}
                              {channelInfo.email && (
                                <p className="text-xs text-blue-600 mt-1">📧 {channelInfo.email}</p>
                              )}
                            </div>
                            <div className="grid grid-cols-3 gap-3 text-center">
                              <div className="bg-white rounded p-2">
                                <p className="text-xs text-gray-600">Abonnés</p>
                                <p className="text-sm font-semibold text-gray-900">
                                  {channelInfo.subscriber_count.toLocaleString()}
                                </p>
                              </div>
                              <div className="bg-white rounded p-2">
                                <p className="text-xs text-gray-600">Vidéos</p>
                                <p className="text-sm font-semibold text-gray-900">
                                  {channelInfo.video_count.toLocaleString()}
                                </p>
                              </div>
                              <div className="bg-white rounded p-2">
                                <p className="text-xs text-gray-600">Vues</p>
                                <p className="text-sm font-semibold text-gray-900">
                                  {channelInfo.view_count.toLocaleString()}
                                </p>
                              </div>
                            </div>
                            {channelInfo.country && (
                              <p className="text-xs text-gray-500">🌍 Pays: {channelInfo.country}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={handleDisconnectYouTube}
                        disabled={disconnecting}
                        className="w-full inline-flex justify-center items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                      >
                        {disconnecting ? (
                          <>
                            <Loader className="h-4 w-4 mr-2 animate-spin" />
                            Déconnexion...
                          </>
                        ) : (
                          <>
                            <XCircle className="h-4 w-4 mr-2" />
                            Se connecter avec un autre compte
                          </>
                        )}
                      </button>
                    </div>
                  ) : null}
                  
                  {youtubeStats && (
                    <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">📊 Statistiques d'Upload</h4>
                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="bg-white rounded p-2">
                          <p className="text-xs text-gray-600">Aujourd'hui</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {youtubeStats.uploads_today}
                          </p>
                        </div>
                        <div className="bg-white rounded p-2">
                          <p className="text-xs text-gray-600">Total</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {youtubeStats.total_uploads}
                          </p>
                        </div>
                        <div className="bg-white rounded p-2">
                          <p className="text-xs text-gray-600">En attente</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {youtubeStats.pending_uploads}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mt-3 text-center">
                        Limite quotidienne: ~{youtubeStats.quota_info.daily_limit} uploads
                      </p>
                    </div>
                  )}
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
