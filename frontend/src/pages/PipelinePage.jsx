import React, { useState, useEffect, useRef } from 'react';
import AgentCard from '../components/AgentCard';
import ProgressBar from '../components/ProgressBar';
import { AGENT_DURATIONS } from '../utils/constants';

export default function PipelinePage({ jobId, onNavigate }) {
  const [agents, setAgents] = useState([
    { name: 'Research Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'Writer Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'Editor Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'SEO Agent', status: 'queued', progress: 0, time: 0 }
  ]);
  
  const [totalProgress, setTotalProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const startTime = useRef(Date.now());

  useEffect(() => {
    const durations = [
      AGENT_DURATIONS.research,
      AGENT_DURATIONS.writer,
      AGENT_DURATIONS.editor,
      AGENT_DURATIONS.seo
    ];
    
    const runAgents = async () => {
      for (let i = 0; i < agents.length; i++) {
        setAgents(prev => prev.map((a, idx) => 
          idx === i ? { ...a, status: 'active', progress: 0 } : a
        ));
        addLog(`${agents[i].name} started`);

        for (let p = 0; p <= 100; p += 10) {
          await new Promise(resolve => setTimeout(resolve, durations[i] * 10));
          setAgents(prev => prev.map((a, idx) =>
            idx === i ? { ...a, progress: p } : a
          ));
          setTotalProgress(Math.floor((i * 100 + p) / 4));
        }

        setAgents(prev => prev.map((a, idx) =>
          idx === i ? { ...a, status: 'complete', progress: 100, time: durations[i] } : a
        ));
        addLog(`${agents[i].name} completed in ${durations[i]}s`);
      }

      setTimeout(() => {
        const mockResult = {
          content: `# The Future of Remote Work in Tech

## Introduction

In today's rapidly evolving landscape, understanding the future of remote work in tech has become increasingly important. This comprehensive guide explores the key aspects, challenges, and opportunities that define this subject.

## Key Points

The fundamental principles can be broken down into several critical components. Each plays a vital role in shaping our understanding and approach to remote work.

### Flexibility and Work-Life Balance

Remote work offers unprecedented flexibility, allowing professionals to design their ideal work environment and schedule.

### Technology Infrastructure

The backbone of remote work relies on robust communication tools, cloud infrastructure, and cybersecurity measures.

### Team Collaboration

New paradigms for collaboration have emerged, leveraging video conferencing, project management tools, and asynchronous communication.

## Conclusion

As we've explored, the future of remote work in tech represents a dynamic and multifaceted subject with exciting possibilities on the horizon.`,
          metadata: {
            word_count: 1523,
            read_time: '7 min read',
            quality_score: 85,
            readability_score: 67,
            seo_score: 82,
            meta_title: 'The Future of Remote Work in Tech',
            meta_description: 'Exploring the evolution of remote work in the technology sector and its impact on productivity.',
            url_slug: 'future-remote-work-tech',
            title_variations: [
              'The Future of Remote Work in Tech',
              'How Remote Work Will Transform Tech Industries',
              'Remote Work in Tech: A Complete 2024 Guide',
              '7 Ways Remote Work is Changing Tech Forever',
              'The Ultimate Guide to Remote Tech Work'
            ]
          },
          performance: {
            total_time: 87.3,
            agent_times: {
              research: 12.4,
              writer: 45.2,
              editor: 18.7,
              seo: 11.0
            },
            token_usage: 4234,
            api_calls: 4,
            cost: 0.00
          }
        };
        onNavigate('results', { result: mockResult });
      }, 1000);
    };

    runAgents();
  }, []);

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time: timestamp, message }]);
  };

  const estimatedTime = Math.max(0, 90 - Math.floor((Date.now() - startTime.current) / 1000));

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Generation in Progress</h2>
        <p className="text-slate-600 dark:text-slate-400">Job #{jobId?.slice(0, 8)}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <ProgressBar 
          progress={totalProgress} 
          label="Overall Progress"
          estimatedTime={estimatedTime}
        />
      </div>

      {/* Agent Pipeline */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 mb-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Agent Pipeline</h3>
        <div className="space-y-4">
          {agents.map((agent, index) => (
            <AgentCard key={index} agent={agent} index={index} />
          ))}
        </div>
      </div>

      {/* Live Console */}
      <div className="bg-slate-900 dark:bg-slate-950 rounded-2xl p-6 border border-slate-800 dark:border-slate-700 shadow-sm">
        <h3 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wide flex items-center gap-2">
          <div className="w-2 h-2 bg-accent-500 rounded-full animate-pulse" />
          System Console
        </h3>
        <div className="space-y-2 font-mono text-xs h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-slate-500">Initializing system...</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-slate-500">[{log.time}]</span>
                <span className="text-accent-400">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}