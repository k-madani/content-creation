import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ProgressBar from '../components/ProgressBar';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function GeneratePage({ mode, onBack, onHome, onGenerate }) {
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [audience, setAudience] = useState('');
  const [contentType, setContentType] = useState('blog post');
  const [wordCount, setWordCount] = useState(1200);
  const [keywords, setKeywords] = useState('');
  const [includeImages, setIncludeImages] = useState(false);
  const [imageCount, setImageCount] = useState(3);
  const [qualityThreshold, setQualityThreshold] = useState(75);
  const [title, setTitle] = useState('');
  const [titleMode, setTitleMode] = useState('generate');
  const [generatedTitles, setGeneratedTitles] = useState([]);
  const [selectedTitle, setSelectedTitle] = useState(0);
  const [serverStatus, setServerStatus] = useState('checking');
  const [isGeneratingTitles, setIsGeneratingTitles] = useState(false);

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState({
    research: { status: 'pending', progress: 0 },
    writing: { status: 'pending', progress: 0 },
    editing: { status: 'pending', progress: 0 },
    seo: { status: 'pending', progress: 0 }
  });

  // Check backend health on mount
  useEffect(() => {
    checkServerHealth();
  }, []);

  const checkServerHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/api/health`);
      if (response.ok) {
        setServerStatus('connected');
      } else {
        setServerStatus('disconnected');
      }
    } catch (error) {
      setServerStatus('disconnected');
    }
  };

  const generateTitles = () => {
    if (!topic.trim()) {
      alert('Please enter a topic first');
      return;
    }

    setIsGeneratingTitles(true);

    // Simulate API delay
    setTimeout(() => {
      const titles = [
        `The Complete Guide to ${topic}`,
        `Understanding ${topic}: Key Insights for 2024`,
        `${topic}: Everything You Need to Know`,
        `Mastering ${topic}: Expert Tips and Strategies`,
        `${topic} Explained: A Comprehensive Overview`
      ];
      
      setGeneratedTitles(titles);
      setIsGeneratingTitles(false);
    }, 800);
  };

  const handleGenerate = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    if (serverStatus === 'disconnected') {
      alert('Backend server is not running. Please start it with: python server.py');
      return;
    }

    setIsGenerating(true);

    // Reset progress
    setProgress({
      research: { status: 'pending', progress: 0 },
      writing: { status: 'pending', progress: 0 },
      editing: { status: 'pending', progress: 0 },
      seo: { status: 'pending', progress: 0 }
    });

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          tone,
          audience: mode === 'custom' ? audience : undefined,
          contentType: mode === 'custom' ? contentType : undefined,
          wordCount,
          keywords: keywords.split(',').map(k => k.trim()).filter(Boolean),
          includeImages: mode !== 'express' ? includeImages : false,
          imageCount: includeImages ? imageCount : 0,
          qualityThreshold: mode === 'custom' ? qualityThreshold : 75,
          title: titleMode === 'custom' ? title : generatedTitles[selectedTitle]
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const { jobId } = await response.json();
      console.log('✓ Job created:', jobId);

      const eventSource = new EventSource(`${API_URL}/api/generate/${jobId}/stream`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('SSE Event:', data.type, data.stage || '');

          if (data.type === 'progress') {
            setProgress(prev => ({
              ...prev,
              [data.stage]: {
                status: data.status,
                progress: data.progress,
                message: data.message
              }
            }));
          }

          if (data.type === 'complete') {
            console.log('✓ Generation complete');
            eventSource.close();
            setIsGenerating(false);
            onGenerate(data);
          }

          if (data.type === 'error') {
            console.error('✗ Generation error:', data.message);
            eventSource.close();
            setIsGenerating(false);
            alert('Generation failed: ' + data.message);
          }
        } catch (err) {
          console.error('Failed to parse SSE data:', err);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        eventSource.close();
        setIsGenerating(false);
        
        const errorMsg = serverStatus === 'disconnected' 
          ? 'Backend server is not running. Please start it with: python server.py'
          : 'Connection lost. Please check your connection and try again.';
        
        alert(errorMsg);
      };

    } catch (error) {
      console.error('Generation error:', error);
      setIsGenerating(false);
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onBack={onBack}
        onLogoClick={onHome}
        showBackButton={true}
      />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Server Status Banner */}
        {serverStatus === 'disconnected' && !isGenerating && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p className="text-red-800 font-semibold">⚠️ Backend server is not running</p>
                <p className="text-red-700 text-sm mt-1">
                  Please start the server in a terminal:
                </p>
                <code className="block bg-red-100 text-red-900 px-3 py-2 rounded mt-2 text-sm font-mono">
                  python server.py
                </code>
              </div>
            </div>
          </div>
        )}

        {serverStatus === 'connected' && !isGenerating && (
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-3 mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-green-800 font-medium text-sm">✓ Connected to backend server</p>
          </div>
        )}

        {!isGenerating ? (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-3xl font-display font-bold mb-8" style={{ color: '#072e57' }}>What do you want to write about?</h2>

            <div className="space-y-6">
              {/* Topic - ALL MODES */}
              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Topic *</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Machine Learning in Healthcare"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  style={{ color: '#072e57' }}
                />
              </div>

              {/* Tone - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Tone</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="technical">Technical</option>
                    <option value="conversational">Conversational</option>
                    {mode === 'custom' && <option value="formal">Formal</option>}
                  </select>
                </div>
              )}

              {/* Audience - CUSTOM ONLY */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Target Audience</label>
                  <input
                    type="text"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    placeholder="e.g., tech professionals, general audience"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  />
                </div>
              )}

              {/* Content Type - CUSTOM ONLY */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Content Type</label>
                  <select
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  >
                    <option value="blog post">Blog Post</option>
                    <option value="article">Article</option>
                    <option value="guide">Guide</option>
                    <option value="listicle">Listicle</option>
                    <option value="review">Review</option>
                  </select>
                </div>
              )}

              {/* Title - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Title</label>
                  <div className="flex gap-3 mb-3">
                    <button
                      type="button"
                      onClick={() => setTitleMode('generate')}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        titleMode === 'generate' 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      style={titleMode === 'generate' ? {} : { color: '#072e57' }}
                    >
                      AI Generate
                    </button>
                    <button
                      type="button"
                      onClick={() => setTitleMode('custom')}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        titleMode === 'custom' 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      style={titleMode === 'custom' ? {} : { color: '#072e57' }}
                    >
                      Custom
                    </button>
                  </div>

                  {titleMode === 'generate' ? (
                    <div>
                      {generatedTitles.length === 0 ? (
                        <button
                          type="button"
                          onClick={generateTitles}
                          disabled={!topic.trim() || isGeneratingTitles}
                          className="w-full px-4 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-gray-600 font-medium"
                        >
                          {isGeneratingTitles ? (
                            <span className="flex items-center justify-center gap-2">
                              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Generating Titles...
                            </span>
                          ) : (
                            'Generate Title Options'
                          )}
                        </button>
                      ) : (
                        <div className="space-y-2">
                          {generatedTitles.map((t, idx) => (
                            <label 
                              key={idx} 
                              className={`flex items-start gap-3 p-4 border-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-all ${
                                selectedTitle === idx ? 'border-primary bg-blue-50' : 'border-gray-200'
                              }`}
                            >
                              <input
                                type="radio"
                                name="title"
                                checked={selectedTitle === idx}
                                onChange={() => setSelectedTitle(idx)}
                                className="mt-1 w-4 h-4 text-primary focus:ring-primary"
                              />
                              <span className="text-sm flex-1" style={{ color: '#072e57' }}>{t}</span>
                            </label>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Enter custom title"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      style={{ color: '#072e57' }}
                    />
                  )}
                </div>
              )}

              {/* Word Count - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Word Count</label>
                  <input
                    type="number"
                    value={wordCount}
                    onChange={(e) => setWordCount(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  />
                </div>
              )}

              {/* Images - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>Include Images?</label>
                  <div className="flex gap-3 mb-3">
                    <button
                      type="button"
                      onClick={() => setIncludeImages(true)}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        includeImages 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      style={includeImages ? {} : { color: '#072e57' }}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setIncludeImages(false)}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        !includeImages 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      style={!includeImages ? {} : { color: '#072e57' }}
                    >
                      No
                    </button>
                  </div>
                  {includeImages && (
                    <select
                      value={imageCount}
                      onChange={(e) => setImageCount(parseInt(e.target.value))}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      style={{ color: '#072e57' }}
                    >
                      <option value={1}>1 image</option>
                      <option value={2}>2 images</option>
                      <option value={3}>3 images</option>
                      <option value={4}>4 images</option>
                      <option value={5}>5 images</option>
                    </select>
                  )}
                </div>
              )}

              {/* Keywords - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>
                    Keywords (comma-separated, optional)
                  </label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="e.g., AI, healthcare, innovation"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  />
                </div>
              )}

              {/* Quality Threshold - CUSTOM ONLY */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#072e57' }}>
                    Quality Threshold (70-90)
                  </label>
                  <input
                    type="number"
                    min="70"
                    max="90"
                    value={qualityThreshold}
                    onChange={(e) => setQualityThreshold(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    style={{ color: '#072e57' }}
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Higher threshold = better quality but may require regeneration
                  </p>
                </div>
              )}

              <button
                onClick={handleGenerate}
                disabled={serverStatus === 'disconnected'}
                className="w-full px-6 py-4 bg-primary text-white rounded-lg hover:bg-blue-900 transition-all font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {serverStatus === 'disconnected' ? 'Server Not Connected' : 'Generate Content'}
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-2xl font-bold mb-8" style={{ color: '#072e57' }}>Generating your content...</h2>

            <div className="space-y-6">
              {Object.entries(progress).map(([stage, data]) => (
                <ProgressBar key={stage} stage={stage} data={data} />
              ))}
            </div>

            <p className="text-sm text-gray-500 text-center mt-8">
              This usually takes about 45-60 seconds
            </p>
          </div>
        )}
      </div>
    </div>
  );
}