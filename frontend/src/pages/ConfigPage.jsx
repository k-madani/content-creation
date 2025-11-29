import React, { useState } from 'react';
import { CONTENT_TYPES, TONES, AUDIENCES, API_URL } from '../utils/constants';
import { ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';

export default function ConfigPage({ onNavigate }) {
  const [formData, setFormData] = useState({
    topic: '',
    word_count: 1500,
    content_type: 'blog post',
    audience: 'general readers',
    tone: 'professional',
    keywords: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!formData.topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Call real backend API
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: formData.topic,
          word_count: formData.word_count,
          content_type: formData.content_type,
          audience: formData.audience,
          tone: formData.tone,
          keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean)
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create generation job');
      }

      const data = await response.json();
      
      // Navigate to pipeline page with real job ID
      onNavigate('pipeline', { jobId: data.job_id });
      
    } catch (err) {
      console.error('Generation error:', err);
      setError(err.message || 'Failed to start generation');
      setIsSubmitting(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button
        onClick={() => onNavigate('dashboard')}
        className="mb-6 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 flex items-center gap-2 group transition"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        Back to Dashboard
      </button>

      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-8 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">Configure Your Content</h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8">Specify your requirements and let AI agents handle the rest</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="space-y-6">
          {/* Topic Input */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Topic / Title <span className="text-primary-600 dark:text-primary-400">*</span>
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => handleChange('topic', e.target.value)}
              placeholder="e.g., The Future of Remote Work in Tech"
              disabled={isSubmitting}
              className="w-full px-4 py-3 border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 rounded-xl focus:border-primary-500 dark:focus:border-primary-400 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-900/30 outline-none transition text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 disabled:opacity-50"
            />
          </div>

          {/* Content Type & Tone */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                Content Type
              </label>
              <select
                value={formData.content_type}
                onChange={(e) => handleChange('content_type', e.target.value)}
                disabled={isSubmitting}
                className="w-full px-4 py-3 border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 rounded-xl focus:border-primary-500 dark:focus:border-primary-400 outline-none transition text-slate-900 dark:text-slate-100 disabled:opacity-50"
              >
                {CONTENT_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                Tone
              </label>
              <select
                value={formData.tone}
                onChange={(e) => handleChange('tone', e.target.value)}
                disabled={isSubmitting}
                className="w-full px-4 py-3 border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 rounded-xl focus:border-primary-500 dark:focus:border-primary-400 outline-none transition text-slate-900 dark:text-slate-100 disabled:opacity-50"
              >
                {TONES.map(tone => (
                  <option key={tone} value={tone}>{tone}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Audience */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Target Audience
            </label>
            <select
              value={formData.audience}
              onChange={(e) => handleChange('audience', e.target.value)}
              disabled={isSubmitting}
              className="w-full px-4 py-3 border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 rounded-xl focus:border-primary-500 dark:focus:border-primary-400 outline-none transition text-slate-900 dark:text-slate-100 disabled:opacity-50"
            >
              {AUDIENCES.map(aud => (
                <option key={aud} value={aud}>{aud}</option>
              ))}
            </select>
          </div>

          {/* Word Count Slider */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Target Word Count: <span className="text-primary-600 dark:text-primary-400">{formData.word_count}</span> words
            </label>
            <input
              type="range"
              min="500"
              max="3500"
              step="100"
              value={formData.word_count}
              onChange={(e) => handleChange('word_count', parseInt(e.target.value))}
              disabled={isSubmitting}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-600 dark:accent-primary-500 disabled:opacity-50"
            />
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-2">
              <span>Quick Read (500)</span>
              <span>Standard (1500)</span>
              <span>In-Depth (3500)</span>
            </div>
          </div>

          {/* Keywords */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              SEO Keywords <span className="text-slate-500 dark:text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={formData.keywords}
              onChange={(e) => handleChange('keywords', e.target.value)}
              placeholder="keyword1, keyword2, keyword3"
              disabled={isSubmitting}
              className="w-full px-4 py-3 border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 rounded-xl focus:border-primary-500 dark:focus:border-primary-400 outline-none transition text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 disabled:opacity-50"
            />
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Separate keywords with commas</p>
          </div>

          {/* Estimated Info */}
          <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl p-4">
            <div className="text-sm text-primary-900 dark:text-primary-100">
              <span className="font-semibold">Estimated:</span> ~90 seconds • 4 agents • $0.00 cost
            </div>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!formData.topic.trim() || isSubmitting}
            className="w-full py-4 bg-primary-600 dark:bg-primary-500 text-white rounded-xl font-semibold text-lg hover:bg-primary-700 dark:hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex items-center justify-center gap-2 group"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Starting Generation...
              </>
            ) : (
              <>
                Start Generation
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}