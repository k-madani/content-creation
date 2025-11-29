import React, { useState } from 'react';
import Header from '../components/Header';
import { ArrowRight } from 'lucide-react';

export default function Dashboard({ onNavigate }) {
  const [hoveredCard, setHoveredCard] = useState(null);

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      {/* Header */}
      <div className="border-b border-slate-100 dark:border-slate-900">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <Header />
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6">
        {/* Hero - Minimal but Impactful */}
        <div className="pt-32 pb-20 text-center relative">
          <div className="inline-block px-4 py-1.5 bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 text-sm rounded-full mb-8 border border-slate-200 dark:border-slate-800">
            Multi-Agent AI System
          </div>

          <h1 className="text-7xl md:text-8xl font-bold mb-8 leading-none tracking-tight">
            <span className="text-slate-900 dark:text-white">Create</span>
            <br />
            <span className="text-slate-400 dark:text-slate-600">Content</span>
            <br />
            <span className="bg-gradient-to-r from-primary-600 to-accent-600 dark:from-primary-400 dark:to-accent-400 bg-clip-text text-transparent">
              Effortlessly
            </span>
          </h1>

          <p className="text-lg text-slate-600 dark:text-slate-400 mb-12 max-w-xl mx-auto">
            AI-powered writing assistant that produces publication-ready articles in 90 seconds
          </p>

          <button
            onClick={() => onNavigate('config')}
            className="group inline-flex items-center gap-2 px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-medium hover:-translate-y-0.5 transition-all duration-200 shadow-lg hover:shadow-2xl"
          >
            Get Started
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
          </button>

          <div className="flex items-center justify-center gap-6 mt-8 text-sm text-slate-500 dark:text-slate-500">
            <span>Free forever</span>
            <span>•</span>
            <span>No signup</span>
            <span>•</span>
            <span>Start instantly</span>
          </div>
        </div>

        {/* Value Props - Hover-Interactive Cards */}
        <div className="grid md:grid-cols-3 gap-8 pb-24">
          {[
            { 
              id: 'free',
              stat: '$0', 
              label: 'Forever Free',
              desc: 'No subscriptions. No credit cards. Just free, unlimited content generation.',
              accent: 'from-accent-500 to-accent-600'
            },
            { 
              id: 'fast',
              stat: '90s', 
              label: 'Lightning Fast',
              desc: 'Four AI agents working in parallel to generate your content quickly.',
              accent: 'from-primary-500 to-primary-600'
            },
            { 
              id: 'quality',
              stat: '97%', 
              label: 'Highly Reliable',
              desc: 'Consistent quality with intelligent fallback mechanisms built in.',
              accent: 'from-accent-500 to-primary-600'
            }
          ].map((item, i) => (
            <div
              key={i}
              onMouseEnter={() => setHoveredCard(item.id)}
              onMouseLeave={() => setHoveredCard(null)}
              className="group relative bg-slate-50 dark:bg-slate-900 rounded-2xl p-8 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-300 cursor-default overflow-hidden"
            >
              {/* Hover gradient effect */}
              <div className={`absolute inset-0 bg-gradient-to-br ${item.accent} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
              
              <div className="relative">
                <div className={`text-6xl font-bold mb-4 transition-all duration-300 ${
                  hoveredCard === item.id 
                    ? `bg-gradient-to-r ${item.accent} bg-clip-text text-transparent`
                    : 'text-slate-900 dark:text-white'
                }`}>
                  {item.stat}
                </div>
                <div className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  {item.label}
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {item.desc}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Process - Ultra Minimal */}
        <div className="pb-24">
          <div className="relative">
            <div className="absolute top-8 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-800 to-transparent" />
            
            <div className="grid grid-cols-4 gap-4 relative">
              {['Research', 'Write', 'Edit', 'Publish'].map((step, i) => (
                <div key={i} className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 flex items-center justify-center text-lg font-bold text-slate-400 dark:text-slate-600 hover:border-primary-500 dark:hover:border-primary-500 hover:text-primary-600 dark:hover:text-primary-400 hover:scale-110 transition-all duration-200 cursor-default">
                    {i + 1}
                  </div>
                  <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    {step}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Secondary CTA - Subtle */}
        <div className="text-center pb-32">
          <button
            onClick={() => onNavigate('config')}
            className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-medium inline-flex items-center gap-2 group transition-colors duration-200"
          >
            Try it now
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
          </button>
        </div>
      </div>
    </div>
  );
}