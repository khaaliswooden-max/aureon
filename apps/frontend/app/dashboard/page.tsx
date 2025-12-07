'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  TrendingUp, Target, Shield, AlertTriangle, 
  ArrowRight, RefreshCw, CheckCircle, Clock 
} from 'lucide-react'
import { StatsCard } from '@/components/StatsCard'
import { api } from '@/lib/api'

interface DashboardStats {
  totalOpportunities: number
  byNoticeType: Record<string, number>
  bySetAside: Record<string, number>
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchStats = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await api.getOpportunityStats()
      setStats({
        totalOpportunities: data.total_active,
        byNoticeType: data.by_notice_type,
        bySetAside: data.by_set_aside,
      })
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching stats:', err)
      setError('Unable to load dashboard stats')
      // Set mock stats as fallback
      setStats({
        totalOpportunities: 150,
        byNoticeType: { 'Solicitation': 80, 'Presolicitation': 40, 'Sources Sought': 30 },
        bySetAside: { 'Small Business': 60, '8(a)': 25, 'SDVOSB': 20, 'unrestricted': 45 },
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  const statCards = stats ? [
    { 
      label: 'Active Opportunities', 
      value: stats.totalOpportunities.toLocaleString(), 
      change: 'Live from SAM.gov',
      icon: Target,
    },
    { 
      label: 'Small Business Set-Asides', 
      value: (stats.bySetAside['Small Business'] || 0).toString(), 
      change: 'SB opportunities',
      icon: TrendingUp,
    },
    { 
      label: '8(a) Opportunities', 
      value: (stats.bySetAside['8(a)'] || stats.bySetAside['8A'] || 0).toString(), 
      change: '8(a) set-asides',
      icon: Shield,
    },
    { 
      label: 'Solicitations', 
      value: (stats.byNoticeType['Solicitation'] || 0).toString(), 
      change: 'Active solicitations',
      icon: CheckCircle,
    },
  ] : []

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-display font-bold text-slate-100 mb-2">
            Dashboard
          </h1>
          <p className="text-slate-400">
            Overview of your procurement intelligence
          </p>
        </div>
        <button
          onClick={fetchStats}
          disabled={isLoading}
          className="btn-secondary"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {isLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-4 bg-cosmos-700/50 rounded w-1/2 mb-3"></div>
                <div className="h-8 bg-cosmos-700/50 rounded w-3/4"></div>
              </div>
            ))}
          </>
        ) : (
          statCards.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
            >
              <StatsCard {...stat} />
            </motion.div>
          ))
        )}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid md:grid-cols-3 gap-6"
      >
        <Link href="/opportunities" className="card-interactive p-6 group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-aureon-500/20 flex items-center justify-center">
              <Target className="w-6 h-6 text-aureon-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-100 group-hover:text-aureon-300 transition-colors">
                Browse Opportunities
              </h3>
              <p className="text-sm text-slate-400">
                Find and analyze opportunities
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-aureon-400 group-hover:translate-x-1 transition-all" />
          </div>
        </Link>

        <Link href="/organizations" className="card-interactive p-6 group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <Shield className="w-6 h-6 text-emerald-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-100 group-hover:text-emerald-300 transition-colors">
                Organization Profile
              </h3>
              <p className="text-sm text-slate-400">
                Configure your capabilities
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
          </div>
        </Link>

        <div className="card p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-cosmos-500/20 flex items-center justify-center">
              <Clock className="w-6 h-6 text-cosmos-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-100">
                Last Updated
              </h3>
              <p className="text-sm text-slate-400">
                {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Not synced'}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Notice Types Breakdown */}
      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6"
        >
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Opportunities by Type
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm text-slate-400 mb-3">Notice Types</h3>
              <div className="space-y-2">
                {Object.entries(stats.byNoticeType).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-slate-300">{type || 'Unspecified'}</span>
                    <span className="text-slate-400 font-mono">{count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm text-slate-400 mb-3">Set-Aside Types</h3>
              <div className="space-y-2">
                {Object.entries(stats.bySetAside).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-slate-300">{type || 'Unrestricted'}</span>
                    <span className="text-slate-400 font-mono">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span className="text-amber-300">{error}</span>
        </motion.div>
      )}
    </div>
  )
}
