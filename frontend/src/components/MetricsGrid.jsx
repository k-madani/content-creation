import React from 'react';
import StatsCard from './StatsCard';

export default function MetricsGrid({ metrics, icons }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {metrics.map((metric, index) => (
        <StatsCard
          key={index}
          icon={icons ? icons[index] : null}
          label={metric.label}
          value={metric.value}
          description={metric.description}
          color={metric.color || 'indigo'}
        />
      ))}
    </div>
  );
}