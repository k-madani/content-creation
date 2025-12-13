import { useState } from 'react';
import Header from '../components/Header';
import ProgressBar from '../components/ProgressBar';

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

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState({
    research: { status: 'pending', progress: 0 },
    writing: { status: 'pending', progress: 0 },
    editing: { status: 'pending', progress: 0 },
    seo: { status: 'pending', progress: 0 }
  });

  const handleGenerate = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
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

      const { jobId } = await response.json();

      const eventSource = new EventSource(`http://localhost:8000/api/generate/${jobId}/stream`);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

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
          eventSource.close();
          setIsGenerating(false);
          onGenerate(data);
        }

        if (data.type === 'error') {
          eventSource.close();
          setIsGenerating(false);
          alert('Generation failed: ' + data.message);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsGenerating(false);
        alert('Connection error');
      };

    } catch (error) {
      setIsGenerating(false);
      alert('Error: ' + error.message);
    }
  };

  const generateTitles = () => {
    setGeneratedTitles([
      `The Complete Guide to ${topic}`,
      `Understanding ${topic}: Key Insights for 2025`,
      `${topic}: Everything You Need to Know`,
      `Mastering ${topic}: Expert Tips and Strategies`,
      `${topic}: A Comprehensive Overview`
    ]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onBack={onBack}
        onLogoClick={onHome}
        showBackButton={true}
      />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {!isGenerating ? (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-3xl font-display font-bold mb-8 text-gray-900">What do you want to write about?</h2>

            <div className="space-y-6">
              {/* Topic - ALL MODES */}
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700">Topic *</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Machine Learning in Healthcare"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                />
              </div>

              {/* Tone - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Tone</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
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
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Target Audience</label>
                  <input
                    type="text"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    placeholder="e.g., tech professionals, general audience"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                  />
                </div>
              )}

              {/* Content Type - CUSTOM ONLY */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Content Type</label>
                  <select
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
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
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Title</label>
                  <div className="flex gap-3 mb-3">
                    <button
                      type="button"
                      onClick={() => setTitleMode('generate')}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        titleMode === 'generate' 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                    >
                      AI Generate
                    </button>
                    <button
                      type="button"
                      onClick={() => setTitleMode('custom')}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        titleMode === 'custom' 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
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
                          disabled={!topic.trim()}
                          className="w-full px-4 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-gray-600 font-medium"
                        >
                          Generate Title Options
                        </button>
                      ) : (
                        <div className="space-y-2">
                          {generatedTitles.map((t, idx) => (
                            <label key={idx} className="flex items-start gap-3 p-4 border-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-all">
                              <input
                                type="radio"
                                name="title"
                                checked={selectedTitle === idx}
                                onChange={() => setSelectedTitle(idx)}
                                className="mt-1 w-4 h-4 text-primary focus:ring-primary"
                              />
                              <span className="text-sm text-gray-900 flex-1">{t}</span>
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
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                    />
                  )}
                </div>
              )}

              {/* Word Count - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Word Count</label>
                  <input
                    type="number"
                    value={wordCount}
                    onChange={(e) => setWordCount(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                  />
                </div>
              )}

              {/* Images - GUIDED & CUSTOM */}
              {(mode === 'guided' || mode === 'custom') && (
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-700">Include Images?</label>
                  <div className="flex gap-3 mb-3">
                    <button
                      type="button"
                      onClick={() => setIncludeImages(true)}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        includeImages 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setIncludeImages(false)}
                      className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                        !includeImages 
                          ? 'border-primary bg-primary text-white' 
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                    >
                      No
                    </button>
                  </div>
                  {includeImages && (
                    <select
                      value={imageCount}
                      onChange={(e) => setImageCount(parseInt(e.target.value))}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
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
                  <label className="block text-sm font-semibold mb-2 text-gray-700">
                    Keywords (comma-separated, optional)
                  </label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="e.g., AI, healthcare, innovation"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                  />
                </div>
              )}

              {/* Quality Threshold - CUSTOM ONLY */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-700">
                    Quality Threshold (70-90)
                  </label>
                  <input
                    type="number"
                    min="70"
                    max="90"
                    value={qualityThreshold}
                    onChange={(e) => setQualityThreshold(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-gray-900"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Higher threshold = better quality but may require regeneration
                  </p>
                </div>
              )}

              <button
                onClick={handleGenerate}
                className="w-full px-6 py-4 bg-primary text-white rounded-lg hover:bg-blue-900 transition-all font-semibold text-lg shadow-lg"
              >
                Generate Content
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-2xl font-bold mb-8 text-gray-900">Generating your content...</h2>

            <div className="space-y-6">
              {Object.entries(progress).map(([stage, data]) => (
                <ProgressBar key={stage} stage={stage} data={data} />
              ))}
            </div>

            <p className="text-sm text-gray-500 text-center mt-8">
              This usually takes about 90 seconds
            </p>
          </div>
        )}
      </div>
    </div>
  );
}