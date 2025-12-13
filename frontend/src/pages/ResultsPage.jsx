import Header from '../components/Header';

export default function ResultsPage({ data, onBack, onHome }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(data?.content || '');
    alert('Copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onBack={onBack}
        onLogoClick={onHome}
        showBackButton={true}
        action={
          <button 
            onClick={handleCopy}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-800"
          >
            Copy to Clipboard
          </button>
        }
      />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Stats */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{data?.metadata?.wordCount || 0}</div>
            <div className="text-sm text-gray-500">Words</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{data?.metadata?.qualityScore || 0}</div>
            <div className="text-sm text-gray-500">Quality Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">90s</div>
            <div className="text-sm text-gray-500">Generation Time</div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap font-sans">
              {data?.content || 'No content generated'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}