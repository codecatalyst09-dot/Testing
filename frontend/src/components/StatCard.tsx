import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  colorTheme?: 'blue' | 'purple' | 'amber' | 'rose' | 'emerald' | 'slate';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  colorTheme = 'blue',
  onClick,
}) => {
  const getThemeStyles = () => {
    switch (colorTheme) {
      case 'purple':
        return {
          iconBg: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
          valColor: 'text-purple-400',
        };
      case 'amber':
        return {
          iconBg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
          valColor: 'text-amber-400',
        };
      case 'rose':
        return {
          iconBg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
          valColor: 'text-rose-400',
        };
      case 'emerald':
        return {
          iconBg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
          valColor: 'text-emerald-400',
        };
      case 'slate':
        return {
          iconBg: 'bg-slate-800 text-slate-300 border-slate-700',
          valColor: 'text-slate-200',
        };
      case 'blue':
      default:
        return {
          iconBg: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
          valColor: 'text-blue-400',
        };
    }
  };

  const theme = getThemeStyles();

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl bg-slate-850 border border-slate-800 shadow-sm transition-all ${
        onClick ? 'cursor-pointer hover:border-slate-700 hover:bg-slate-800/80' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg border ${theme.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className={`text-2xl font-bold mt-2 ${theme.valColor}`}>{value}</div>
      {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
    </div>
  );
};
