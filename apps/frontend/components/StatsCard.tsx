'use client'

interface StatsCardProps {
  label: string
  value: string
  change?: string
}

export function StatsCard({ label, value, change }: StatsCardProps) {
  return (
    <div className="card p-6 group hover:border-cosmos-700/70 transition-colors">
      <div className="text-sm text-slate-500 mb-2">{label}</div>
      <div className="text-3xl font-display font-bold text-slate-100 mb-1 group-hover:text-gradient transition-all">
        {value}
      </div>
      {change && (
        <div className="text-xs text-aureon-400">{change}</div>
      )}
    </div>
  )
}

