import { ReactNode } from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

export default function KPICard({ title, value, icon, trend }: KPICardProps) {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-semibold text-muted">{title}</h3>
        <div style={{ color: 'var(--accent-primary)', opacity: 0.8 }}>
          {icon}
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem' }}>
        <span style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {value}
        </span>
        
        {trend && (
          <span className={`text-sm font-semibold ${trend.isPositive ? 'badge-success' : 'badge-danger'} badge`}>
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
