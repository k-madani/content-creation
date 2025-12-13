import Header from '../components/Header';

export default function ModeSelectionPage({ onSelectMode, onHome }) {
  const modes = [
    {
      id: 'express',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Express',
      subtitle: 'Just topic',
      description: 'Quick generation with minimal input. Perfect for getting started fast.',
      features: ['Just enter a topic', 'Auto-detected tone', 'Smart defaults', '< 30 seconds setup']
    },
    {
      id: 'guided',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      title: 'Guided',
      subtitle: 'Step-by-step',
      description: 'Balanced approach with AI assistance. Recommended for most users.',
      features: ['Topic & tone selection', 'AI-generated titles', 'Image options', 'Keyword targeting']
    },
    {
      id: 'custom',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
      ),
      title: 'Custom',
      subtitle: 'Full control',
      description: 'Advanced options for precise control over every aspect of generation.',
      features: ['Audience targeting', 'Content type selection', 'Quality threshold', 'Full customization']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onLogoClick={onHome}
        showBackButton={false}
      />

      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose Your Creation Mode</h1>
          <p className="text-xl text-gray-600">Select the level of control you want</p>
        </div>

        <div className="grid grid-cols-3 gap-8">
          {modes.map((mode) => (
            <button
              key={mode.id}
              onClick={() => onSelectMode(mode.id)}
              className="bg-white rounded-lg border-2 border-gray-200 p-8 hover:border-primary hover:shadow-lg transition-all text-left group"
            >
              <div className="text-gray-600 group-hover:text-primary mb-4 transition-colors">
                {mode.icon}
              </div>
              <h3 className="text-2xl font-bold mb-1">{mode.title}</h3>
              <p className="text-sm text-gray-500 mb-4">{mode.subtitle}</p>
              <p className="text-gray-600 mb-6">{mode.description}</p>
              
              <ul className="space-y-2">
                {mode.features.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                    <svg className="w-4 h-4 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}