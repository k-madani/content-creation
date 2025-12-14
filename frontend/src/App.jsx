import { useState } from 'react';
import LandingPage from './pages/LandingPage';
import ModeSelectionPage from './pages/ModeSelectionPage';
import GeneratePage from './pages/GeneratePage';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  const [currentView, setCurrentView] = useState('landing');
  const [selectedMode, setSelectedMode] = useState(null);
  const [generationData, setGenerationData] = useState(null);

  const goHome = () => setCurrentView('landing');

  return (
    <>
      {currentView === 'landing' && (
        <LandingPage onGetStarted={() => setCurrentView('modeSelection')} />
      )}
      {currentView === 'modeSelection' && (
        <ModeSelectionPage 
          onHome={goHome}
          onSelectMode={(mode) => {
            setSelectedMode(mode);
            setCurrentView('generate');
          }} 
        />
      )}
      {currentView === 'generate' && (
        <GeneratePage 
          mode={selectedMode}
          onBack={() => setCurrentView('modeSelection')}
          onHome={goHome}
          onGenerate={(data) => {
            setGenerationData(data);
            setCurrentView('results');
          }}
        />
      )}
      {currentView === 'results' && (
        <ResultsPage 
          data={generationData}
          onBack={() => setCurrentView('generate')}
          onHome={goHome}
        />
      )}
    </>
  );
}