import React, { useState } from 'react';
import { Copy, Download, Check, FileText, BarChart3, Tags, Clock, ChevronDown, ChevronUp, ArrowLeft, ArrowRight } from 'lucide-react';
import MetricsGrid from '../components/MetricsGrid';

export default function ResultsPage({ result, onNavigate }) {
  const [activeTab, setActiveTab] = useState('performance');
  const [copied, setCopied] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  if (!result) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-slate-600 dark:text-slate-400">Loading results...</div>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(result.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([result.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.metadata.url_slug}.txt`;
    a.click();
  };

  const metrics = [
    {
      label: 'Word Count',
      value: result.metadata.word_count,
      description: result.metadata.read_time,
      color: 'primary'
    },
    {
      label: 'Time',
      value: `${result.performance.total_time}s`,
      description: 'Generation time',
      color: 'primary'
    },
    {
      label: 'SEO Score',
      value: `${result.metadata.seo_score}/100`,
      description: 'Google ready',
      color: 'accent'
    },
    {
      label: 'Quality',
      value: `${result.metadata.quality_score}/100`,
      description: 'Publication ready',
      color: 'accent'
    }
  ];

  const icons = [FileText, Clock, BarChart3, Tags];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Content Ready</h2>
            <span className="px-3 py-1 bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-400 text-sm font-semibold rounded-full border border-accent-200 dark:border-accent-800">
              Complete
            </span>
          </div>
          <p className="text-slate-600 dark:text-slate-400">Your article is ready to publish</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate('dashboard')}
            className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition flex items-center gap-2 group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('config')}
            className="px-4 py-2 bg-primary-600 dark:bg-primary-500 text-white rounded-lg hover:bg-primary-700 dark:hover:bg-primary-600 transition flex items-center gap-2 group"
          >
            New Generation
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* Quality Metrics Bar */}
      <div className="mb-6">
        <MetricsGrid metrics={metrics} icons={icons} />
      </div>

      {/* Main Content Area */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden mb-6 shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">Generated Article</h3>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-sm text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-lg transition"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-slate-200 dark:border-slate-700 max-h-[500px] overflow-y-auto">
            <pre className="whitespace-pre-wrap font-sans text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
              {result.content}
            </pre>
          </div>
        </div>
      </div>

      {/* Analytics Section (Collapsible) */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
        <button
          onClick={() => setShowAnalytics(!showAnalytics)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-900/50 transition"
        >
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <span className="font-semibold text-slate-900 dark:text-slate-100">View Analytics & Metadata</span>
          </div>
          {showAnalytics ? 
            <ChevronUp className="w-5 h-5 text-slate-600 dark:text-slate-400" /> : 
            <ChevronDown className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          }
        </button>

        {showAnalytics && (
          <div className="border-t border-slate-200 dark:border-slate-700">
            <div className="px-6 pt-4 flex gap-4 border-b border-slate-200 dark:border-slate-700">
              {['performance', 'seo', 'titles'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-3 px-2 font-medium text-sm border-b-2 transition capitalize ${
                    activeTab === tab
                      ? 'border-primary-600 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="p-6">
              {activeTab === 'performance' && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">Execution Breakdown</h4>
                    <div className="space-y-2">
                      {Object.entries(result.performance.agent_times).map(([agent, time]) => (
                        <div key={agent}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="capitalize text-slate-700 dark:text-slate-300">{agent} Agent</span>
                            <span className="font-semibold text-slate-900 dark:text-slate-100">{time}s ({Math.round(time / result.performance.total_time * 100)}%)</span>
                          </div>
                          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full transition-all"
                              style={{ width: `${(time / result.performance.total_time * 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                      <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">Total Time</div>
                      <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{result.performance.total_time}s</div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                      <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">Token Usage</div>
                      <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{result.performance.token_usage}</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'seo' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Meta Title</label>
                    <div className="p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-800 dark:text-slate-200">
                      {result.metadata.meta_title}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Meta Description</label>
                    <div className="p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-800 dark:text-slate-200">
                      {result.metadata.meta_description}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">URL Slug</label>
                    <div className="p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-mono text-slate-800 dark:text-slate-200">
                      /{result.metadata.url_slug}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'titles' && (
                <div className="space-y-3">
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                    Alternative title options for A/B testing
                  </p>
                  {result.metadata.title_variations.map((title, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition">
                      <div>
                        <div className="font-medium text-slate-900 dark:text-slate-100">{title}</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Variation {i + 1}</div>
                      </div>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(title);
                        }}
                        className="px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-lg transition"
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}