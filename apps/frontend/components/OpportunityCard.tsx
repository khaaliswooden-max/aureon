'use client'

import { formatDistanceToNow, format } from 'date-fns'
import { Calendar, MapPin, Building2, DollarSign, Clock } from 'lucide-react'
import { clsx } from 'clsx'

interface OpportunityCardProps {
  id: string
  title: string
  description?: string
  naicsCode?: string
  naicsDescription?: string
  setAsideType?: string
  contractingOfficeName?: string
  placeOfPerformanceState?: string
  placeOfPerformanceCity?: string
  responseDeadline?: string
  postedDate?: string
  estimatedValueMin?: number
  estimatedValueMax?: number
  relevanceScore?: number
  onClick?: () => void
}

export function OpportunityCard({
  title,
  description,
  naicsCode,
  naicsDescription,
  setAsideType,
  contractingOfficeName,
  placeOfPerformanceState,
  placeOfPerformanceCity,
  responseDeadline,
  postedDate,
  estimatedValueMin,
  estimatedValueMax,
  relevanceScore,
  onClick,
}: OpportunityCardProps) {
  const deadline = responseDeadline ? new Date(responseDeadline) : null
  const posted = postedDate ? new Date(postedDate) : null
  const isUrgent = deadline && deadline.getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000

  const formatValue = (value?: number) => {
    if (!value) return null
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`
    return `$${value.toFixed(0)}`
  }

  const scoreColor = relevanceScore
    ? relevanceScore >= 0.8
      ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
      : relevanceScore >= 0.6
      ? 'text-aureon-400 border-aureon-500/30 bg-aureon-500/10'
      : relevanceScore >= 0.4
      ? 'text-amber-400 border-amber-500/30 bg-amber-500/10'
      : 'text-rose-400 border-rose-500/30 bg-rose-500/10'
    : ''

  return (
    <div
      onClick={onClick}
      className="card-interactive p-6 space-y-4"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-slate-100 line-clamp-2 mb-2">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-slate-400 line-clamp-2">
              {description}
            </p>
          )}
        </div>
        
        {relevanceScore !== undefined && (
          <div className={clsx('flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center border', scoreColor)}>
            <span className="text-lg font-bold">{Math.round(relevanceScore * 100)}</span>
          </div>
        )}
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-2">
        {naicsCode && (
          <span className="badge-blue">
            {naicsCode}
          </span>
        )}
        {setAsideType && (
          <span className="badge-gold">
            {setAsideType}
          </span>
        )}
        {isUrgent && (
          <span className="badge-red">
            Urgent
          </span>
        )}
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        {contractingOfficeName && (
          <div className="flex items-center gap-2 text-slate-400">
            <Building2 className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{contractingOfficeName}</span>
          </div>
        )}
        
        {(placeOfPerformanceCity || placeOfPerformanceState) && (
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">
              {[placeOfPerformanceCity, placeOfPerformanceState].filter(Boolean).join(', ')}
            </span>
          </div>
        )}

        {deadline && (
          <div className={clsx('flex items-center gap-2', isUrgent ? 'text-rose-400' : 'text-slate-400')}>
            <Clock className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">
              Due {formatDistanceToNow(deadline, { addSuffix: true })}
            </span>
          </div>
        )}

        {(estimatedValueMin || estimatedValueMax) && (
          <div className="flex items-center gap-2 text-slate-400">
            <DollarSign className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">
              {formatValue(estimatedValueMin)}
              {estimatedValueMax && estimatedValueMin !== estimatedValueMax && ` - ${formatValue(estimatedValueMax)}`}
            </span>
          </div>
        )}
      </div>

      {/* Footer */}
      {posted && (
        <div className="pt-3 border-t border-cosmos-800/50 flex items-center gap-2 text-xs text-slate-500">
          <Calendar className="w-3.5 h-3.5" />
          <span>Posted {format(posted, 'MMM d, yyyy')}</span>
        </div>
      )}
    </div>
  )
}

