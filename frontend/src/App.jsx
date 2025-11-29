import React, { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import Dashboard from './pages/Dashboard';
import ConfigPage from './pages/ConfigPage';
import PipelinePage from './pages/PipelinePage';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('dashboard');
  const [jobId, setJobId] = useState(null);
  const [jobResult, setJobResult] = useState(null);

  const navigateTo = (screen, data = {}) => {
    setCurrentScreen(screen);
    if (data.jobId) setJobId(data.jobId);
    if (data.result) setJobResult(data.result);
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-white dark:bg-slate-950">
        {currentScreen === 'dashboard' && <Dashboard onNavigate={navigateTo} />}
        {currentScreen === 'config' && <ConfigPage onNavigate={navigateTo} />}
        {currentScreen === 'pipeline' && <PipelinePage jobId={jobId} onNavigate={navigateTo} />}
        {currentScreen === 'results' && <ResultsPage result={jobResult} onNavigate={navigateTo} />}
      </div>
    </ThemeProvider>
  );
}