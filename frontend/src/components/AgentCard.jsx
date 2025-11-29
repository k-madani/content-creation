import React from 'react';
import { CheckCircle, Loader2, Circle } from 'lucide-react';

export default function AgentCard({ agent, index }) {
  const getStatusIcon = (status) => {
    if (status === 'complete') return <CheckCircle className="w-6 h-6 text-accent-600 dark:text-accent-400" />;
    if (status === 'active') return <Loader2 className="w-6 h-6 text-primary-600 dark:text-primary-400 animate-spin" />;
    return <Circle className="w-6 h-6 text-slate-300 dark:text-slate-600" />;
  };

  const getStatusColor = (status) => {
    if (status === 'complete') return 'bg-accent-50 dark:bg-accent-900/20 border-accent-200 dark:border-accent-800';
    if (status === 'active') return 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800';
    return 'bg-slate-50 dark:bg-slate-900/30 border-slate-200 dark:border-slate-700';
  };

  const getStatusText = (status, time) => {
    if (status === 'complete') return `Completed in ${time}s`;
    if (status === 'active') return 'Processing...';
    return 'Waiting in queue';
  };

  return (
    <div className={`border-2 rounded-xl p-4 transition ${getStatusColor(agent.status)}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          {getStatusIcon(agent.status)}
          <div>
            <div className="font-semibold text-slate-900 dark:text-slate-100">
              {index + 1}. {agent.name}
            </div>
            <div className="text-sm text-slate-600 dark:text-slate-400">
              {getStatusText(agent.status, agent.time)}
            </div>
          </div>
        </div>
        {agent.time > 0 && (
          <div className="text-sm font-mono text-slate-700 dark:text-slate-300">
            {agent.time.toFixed(1)}s
          </div>
        )}
      </div>

      {agent.status === 'active' && (
        <div className="mt-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-600 dark:text-slate-400">Progress</span>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{agent.progress}%</span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
            <div
              className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full transition-all"
              style={{ width: `${agent.progress}%` }}
            />
          </div>
        </div>
      )}

      {agent.status === 'complete' && agent.details && (
        <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          {agent.details}
        </div>
      )}
    </div>
  );
}