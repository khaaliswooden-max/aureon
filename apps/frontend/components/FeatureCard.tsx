'use client'

import { LucideIcon } from 'lucide-react'
import { clsx } from 'clsx'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  color?: 'aureon' | 'emerald' | 'cosmos'
}

const colorStyles = {
  aureon: {
    iconBg: 'bg-aureon-500/20',
    iconColor: 'text-aureon-400',
    hoverBorder: 'hover:border-aureon-500/30',
  },
  emerald: {
    iconBg: 'bg-emerald-500/20',
    iconColor: 'text-emerald-400',
    hoverBorder: 'hover:border-emerald-500/30',
  },
  cosmos: {
    iconBg: 'bg-cosmos-500/20',
    iconColor: 'text-cosmos-400',
    hoverBorder: 'hover:border-cosmos-500/30',
  },
}

export function FeatureCard({ icon: Icon, title, description, color = 'aureon' }: FeatureCardProps) {
  const styles = colorStyles[color]

  return (
    <div className={clsx('card-interactive p-8', styles.hoverBorder)}>
      <div className={clsx('w-14 h-14 rounded-2xl flex items-center justify-center mb-6', styles.iconBg)}>
        <Icon className={clsx('w-7 h-7', styles.iconColor)} />
      </div>
      <h3 className="text-xl font-display font-semibold text-slate-100 mb-3">
        {title}
      </h3>
      <p className="text-slate-400 leading-relaxed">
        {description}
      </p>
    </div>
  )
}

