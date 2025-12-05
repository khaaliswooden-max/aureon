'use client'

import { clsx } from 'clsx'

interface ScoreRingProps {
  score: number // 0 to 1
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  label?: string
}

const sizeStyles = {
  sm: { ring: 'w-12 h-12', text: 'text-sm', stroke: 3, radius: 18 },
  md: { ring: 'w-20 h-20', text: 'text-xl', stroke: 4, radius: 32 },
  lg: { ring: 'w-28 h-28', text: 'text-3xl', stroke: 5, radius: 48 },
}

export function ScoreRing({ score, size = 'md', showLabel = true, label }: ScoreRingProps) {
  const styles = sizeStyles[size]
  const circumference = 2 * Math.PI * styles.radius
  const offset = circumference - score * circumference
  
  const getColor = () => {
    if (score >= 0.8) return { stroke: '#10b981', text: 'text-emerald-400' }
    if (score >= 0.6) return { stroke: '#f59e0b', text: 'text-aureon-400' }
    if (score >= 0.4) return { stroke: '#f59e0b', text: 'text-amber-400' }
    return { stroke: '#f43f5e', text: 'text-rose-400' }
  }
  
  const color = getColor()

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={clsx('relative', styles.ring)}>
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={styles.radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={styles.stroke}
            className="text-cosmos-800"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={styles.radius}
            fill="none"
            stroke={color.stroke}
            strokeWidth={styles.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <div className={clsx('absolute inset-0 flex items-center justify-center font-bold', styles.text, color.text)}>
          {Math.round(score * 100)}
        </div>
      </div>
      {showLabel && label && (
        <span className="text-xs text-slate-500">{label}</span>
      )}
    </div>
  )
}

