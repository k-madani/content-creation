import Footer from '../components/Footer';

export default function LandingPage({ onGetStarted }) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#ffffff' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50" style={{ borderBottom: '1px solid #e2e8f0' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center shadow-md" style={{ backgroundColor: '#072e57' }}>
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </div>
            <span className="text-xl font-semibold" style={{ color: '#072e57' }}>ContentFlow</span>
          </div>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg className="w-6 h-6" style={{ color: '#64748b' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>
        </div>
      </header>

      {/* Hero Section - White */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center" style={{ backgroundColor: '#ffffff' }}>
        <div className="max-w-4xl mx-auto">
          <p className="text-sm font-semibold uppercase tracking-wider mb-6" style={{ color: '#2563eb' }}>
            AI Writing Assistant
          </p>
          <h1 className="text-7xl font-display font-bold mb-8 leading-tight" style={{ color: '#072e57' }}>
            Publish quality<br />
            content, <span className="italic font-light" style={{ color: '#64748b' }}>effortlessly</span>
          </h1>
          <p className="text-xl max-w-3xl mx-auto mb-10 leading-relaxed" style={{ color: '#64748b' }}>
            From research to final draft in under two minutes. Let AI handle the heavy lifting while you focus on what matters.
          </p>
          
          {/* Buttons */}
          <div className="flex items-center justify-center gap-4 mb-6">
            <button 
              onClick={onGetStarted}
              type="button"
              className="inline-flex items-center gap-2 px-8 py-4 text-white font-semibold text-base rounded-lg transition-all shadow-lg"
              style={{ backgroundColor: '#072e57' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#0a3d75'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#072e57'}
            >
              Get Started Free
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            
            <button 
              onClick={() => {
                document.getElementById('how-it-works')?.scrollIntoView({ 
                  behavior: 'smooth' 
                });
              }}
              type="button"
              className="inline-flex items-center px-8 py-4 border-2 font-semibold text-base rounded-lg transition-all"
              style={{ borderColor: '#e2e8f0', color: '#072e57', backgroundColor: 'transparent' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#072e57';
                e.currentTarget.style.backgroundColor = '#f8fafc';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              See How It Works
            </button>
          </div>

          <p className="text-sm" style={{ color: '#94a3b8' }}>
            No credit card required • Start writing in seconds
          </p>
        </div>
      </section>

      {/* How It Works - Very Light Gray */}
      <section id="how-it-works" className="py-20" style={{ backgroundColor: '#f8fafc' }}>
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-sm font-semibold uppercase tracking-wider text-center mb-4" style={{ color: '#2563eb' }}>
            How It Works
          </p>
          <h2 className="text-5xl font-display font-bold text-center mb-16" style={{ color: '#072e57' }}>
            Five steps to <span className="italic font-light" style={{ color: '#64748b' }}>publication-ready</span> content
          </h2>
          
          <div className="relative">
            <div className="absolute top-10 left-0 right-0 h-0.5" style={{ width: '80%', margin: '0 auto', backgroundColor: '#e2e8f0' }} />
            
            <div className="grid grid-cols-5 gap-8 relative">
              {[
                { 
                  icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>,
                  num: '01', 
                  title: 'Configure', 
                  desc: 'Specify topic, tone, length, and target audience in seconds' 
                },
                { 
                  icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
                  num: '02', 
                  title: 'Research', 
                  desc: 'AI gathers relevant data, stats, and sources from across the web' 
                },
                { 
                  icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>,
                  num: '03', 
                  title: 'Write', 
                  desc: 'Generates a structured draft optimized for your target audience' 
                },
                { 
                  icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>,
                  num: '04', 
                  title: 'Refine', 
                  desc: 'Polish tone, style, and flow with intelligent suggestions' 
                },
                { 
                  icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>,
                  num: '05', 
                  title: 'Publish', 
                  desc: 'Export to any format or publish directly to your CMS' 
                }
              ].map((step) => (
                <div key={step.num} className="text-center relative z-10">
                  <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-md" style={{ border: '2px solid #e2e8f0', color: '#072e57' }}>
                    {step.icon}
                  </div>
                  <div className="text-xs font-semibold mb-2" style={{ color: '#94a3b8' }}>{step.num}</div>
                  <h3 className="font-bold text-lg mb-3" style={{ color: '#072e57' }}>{step.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: '#64748b' }}>{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features - White */}
      <section className="py-20" style={{ backgroundColor: '#ffffff' }}>
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-sm font-semibold uppercase tracking-wider text-center mb-4" style={{ color: '#2563eb' }}>
            Features
          </p>
          <h2 className="text-5xl font-display font-bold text-center mb-16" style={{ color: '#072e57' }}>
            Built for <span className="italic font-light" style={{ color: '#64748b' }}>modern</span> content teams
          </h2>
          
          <div className="grid grid-cols-2 gap-12">
            {[
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
                title: 'Lightning Fast', 
                desc: 'Generate complete articles in under 90 seconds, not hours.' 
              },
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
                title: 'SEO Optimized', 
                desc: 'Built-in keyword optimization and meta descriptions.' 
              },
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>,
                title: 'Brand Voice', 
                desc: 'Learns your tone and maintains consistency across all content.' 
              },
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>,
                title: 'Fact-Checked', 
                desc: 'AI verifies claims and provides source citations.' 
              },
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>,
                title: 'AI Image Generation', 
                desc: 'Optionally include AI-generated images that complement your content perfectly.' 
              },
              { 
                icon: <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>,
                title: 'Self-Improving AI', 
                desc: 'Unlike other AI tools, ContentForge has standards—it reviews and fixes its own mistakes automatically.' 
              }
            ].map((feature) => (
              <div key={feature.title} className="text-center p-8">
                <div className="flex justify-center mb-5" style={{ color: '#072e57' }}>{feature.icon}</div>
                <h3 className="font-bold text-xl mb-3" style={{ color: '#072e57' }}>{feature.title}</h3>
                <p className="leading-relaxed" style={{ color: '#64748b' }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}