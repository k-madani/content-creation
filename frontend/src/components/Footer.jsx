export default function Footer() {
  return (
    <footer className="bg-white" style={{ borderTop: '1px solid #e2e8f0' }}>
      <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ backgroundColor: '#072e57' }}>
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </div>
          <span className="font-semibold" style={{ color: '#1a4d7a' }}>ContentFlow</span>
        </div>
        <div className="flex gap-8 text-sm" style={{ color: '#64748b' }}>
          <a href="#" className="hover:opacity-70 transition-opacity">Privacy</a>
          <a href="#" className="hover:opacity-70 transition-opacity">Terms</a>
        </div>
        <p className="text-sm" style={{ color: '#94a3b8' }}>© 2024 ContentFlow. Built for modern content teams.</p>
      </div>
    </footer>
  );
}