import React from 'react';

export default function StatsCard({ icon: Icon, label, value, description, color = 'primary' }) {
  const colorClasses = {
    primary: 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 border-primary-100 dark:border-primary-800',
    accent: 'text-accent-600 dark:text-accent-400 bg-accent-50 dark:bg-accent-900/20 border-accent-100 dark:border-accent-800',
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
      {Icon && (
        <div className={`flex items-center gap-2 text-sm font-semibold mb-1 ${colorClasses[color]}`}>
          <Icon className="w-4 h-4" />
          <span className="text-slate-700 dark:text-slate-300">{label}</span>
        </div>
      )}
      {!Icon && <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">{label}</div>}
      <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">{value}</div>
      {description && <div className="text-xs text-slate-500 dark:text-slate-400">{description}</div>}
    </div>
  );
}