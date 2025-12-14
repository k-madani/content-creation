export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo and Brand */}
          <div className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center" 
              style={{ backgroundColor: '#072e57' }}
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </div>
            <span className="font-semibold text-lg" style={{ color: '#072e57' }}>ContentFlow</span>
          </div>

          {/* Links */}
          <div className="flex items-center gap-6">
            <a 
              href="#" 
              className="text-sm font-medium transition-colors hover:opacity-70"
              style={{ color: '#64748b' }}
            >
              Privacy
            </a>
            <a 
              href="#" 
              className="text-sm font-medium transition-colors hover:opacity-70"
              style={{ color: '#64748b' }}
            >
              Terms
            </a>
            <a 
              href="#" 
              className="text-sm font-medium transition-colors hover:opacity-70"
              style={{ color: '#64748b' }}
            >
              Contact
            </a>
          </div>

          {/* Copyright */}
          <p className="text-sm" style={{ color: '#94a3b8' }}>
            © 2024 ContentFlow. Built for modern content teams.
          </p>
        </div>
      </div>
    </footer>
  );
}