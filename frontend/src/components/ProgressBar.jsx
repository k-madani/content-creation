import React from 'react';

export default function ProgressBar({ progress, label, estimatedTime }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          {label}: {progress}%
        </span>
        {estimatedTime !== undefined && (
          <span className="text-sm text-slate-600 dark:text-slate-400">
            Est. remaining: {estimatedTime}s
          </span>
        )}
      </div>
      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3">
        <div
          className="bg-gradient-to-r from-primary-600 to-primary-500 dark:from-primary-500 dark:to-primary-400 h-3 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}