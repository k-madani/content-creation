import React from 'react';
import ThemeToggle from './ThemeToggle';

export default function Header() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-slate-900 dark:bg-white rounded-lg flex items-center justify-center">
          <div className="w-3 h-3 bg-white dark:bg-slate-900 rounded-sm" />
        </div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white tracking-tight">
          ContentFlow
        </h1>
      </div>
      
      <ThemeToggle />
    </div>
  );
}