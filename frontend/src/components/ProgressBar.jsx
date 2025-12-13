export default function ProgressBar({ stage, data }) {
  const stageNames = {
    research: 'Research',
    writing: 'Writing',
    editing: 'Editing',
    seo: 'SEO Optimization'
  };

  const stageIcons = {
    research: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    writing: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
      </svg>
    ),
    editing: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
    ),
    seo: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    )
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-gray-600">{stageIcons[stage]}</span>
          <span className="font-medium">{stageNames[stage]}</span>
        </div>
        {data.status === 'complete' && (
          <span className="text-green-600 font-medium">✓ Complete</span>
        )}
        {data.status === 'working' && (
          <span className="text-blue-600 font-medium">{data.progress}%</span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            data.status === 'complete' ? 'bg-green-600' :
            data.status === 'working' ? 'bg-blue-600' :
            'bg-gray-300'
          }`}
          style={{ width: `${data.progress}%` }}
        />
      </div>
      {data.message && (
        <p className="text-sm text-gray-500 mt-1">{data.message}</p>
      )}
    </div>
  );
}