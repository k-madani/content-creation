import { useState } from 'react';

// Inline Header component
function Header({ onBack, onLogoClick, showBackButton = true, action }) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {showBackButton && onBack && (
            <button 
              onClick={onBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              style={{ color: '#072e57' }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}
          <button 
            onClick={onLogoClick}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div 
              className="w-9 h-9 rounded-lg flex items-center justify-center" 
              style={{ backgroundColor: '#072e57' }}
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </div>
            <span className="text-xl font-semibold" style={{ color: '#072e57' }}>ContentFlow</span>
          </button>
        </div>
        {action && <div>{action}</div>}
      </div>
    </header>
  );
}

export default function ResultsPage({ data, onBack, onHome }) {
  const [copiedImage, setCopiedImage] = useState(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(data?.content || '');
    alert('Content copied to clipboard!');
  };

  const handleCopyImageUrl = (url, index) => {
    navigator.clipboard.writeText(url);
    setCopiedImage(index);
    setTimeout(() => setCopiedImage(null), 2000);
  };

  const images = data?.metadata?.images || [];
  const hasImages = images.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onBack={onBack}
        onLogoClick={onHome}
        showBackButton={true}
        action={
          <button 
            onClick={handleCopy}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
          >
            Copy Content
          </button>
        }
      />

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Stats */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#072e57' }}>
              {data?.metadata?.wordCount || 0}
            </div>
            <div className="text-sm text-gray-500">Words</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#072e57' }}>
              {data?.metadata?.qualityScore || 0}
            </div>
            <div className="text-sm text-gray-500">Quality Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#072e57' }}>
              {data?.metadata?.seoScore || 0}
            </div>
            <div className="text-sm text-gray-500">SEO Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color: '#072e57' }}>
              {data?.metadata?.imageCount || 0}
            </div>
            <div className="text-sm text-gray-500">Images</div>
          </div>
        </div>

        {/* Image Gallery (if images exist) */}
        {hasImages && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-xl font-bold mb-4" style={{ color: '#072e57' }}>
              Generated Images
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {images.map((img, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                  <div className="aspect-square bg-gray-100 relative">
                    <img 
                      src={img.url} 
                      alt={img.alt}
                      title={img.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage Loading...%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  </div>
                  <div className="p-3">
                    <p className="text-sm font-medium mb-1" style={{ color: '#072e57' }}>
                      {img.caption}
                    </p>
                    <p className="text-xs text-gray-500 mb-2">
                      Section: {img.section}
                    </p>
                    <button
                      onClick={() => handleCopyImageUrl(img.url, idx)}
                      className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                      style={{ color: '#072e57' }}
                    >
                      {copiedImage === idx ? '✓ Copied!' : 'Copy URL'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Preview */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold" style={{ color: '#072e57' }}>
              Generated Content
            </h2>
            <span className="text-sm text-gray-500">
              {data?.metadata?.generationTime || 'N/A'}
            </span>
          </div>
          
          <div className="prose max-w-none">
            <div 
              className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed"
              style={{ 
                fontFamily: 'Inter, sans-serif',
                fontSize: '16px',
                lineHeight: '1.8'
              }}
            >
              {data?.content || 'No content generated'}
            </div>
          </div>

          {/* Keywords */}
          {data?.metadata?.keywords && data.metadata.keywords.length > 0 && (
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-semibold mb-3" style={{ color: '#072e57' }}>
                Keywords
              </h3>
              <div className="flex flex-wrap gap-2">
                {data.metadata.keywords.map((keyword, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 bg-blue-50 rounded-full text-sm"
                    style={{ color: '#072e57' }}
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Tone:</span>
                <span className="ml-2 font-medium" style={{ color: '#072e57' }}>
                  {data?.metadata?.tone || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Readability:</span>
                <span className="ml-2 font-medium" style={{ color: '#072e57' }}>
                  {data?.metadata?.readabilityScore || 'N/A'}/10
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}