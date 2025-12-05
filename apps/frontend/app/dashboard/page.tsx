'use client'

import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Target, 
  AlertTriangle, 
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart
} from 'lucide-react'
import { ScoreRing } from '@/components/ScoreRing'

const pipelineStats = [
  { label: 'Total Pipeline', value: 24, change: +5, period: 'this week' },
  { label: 'High Relevance', value: 8, change: +2, period: 'score > 80%' },
  { label: 'Due This Week', value: 3, change: -1, period: 'urgent' },
  { label: 'Under Review', value: 12, change: 0, period: 'bid/no-bid' },
]

const recentScores = [
  { opportunity: 'Cloud Migration Services', score: 0.92, risk: 'low', trend: 'up' },
  { opportunity: 'Cybersecurity Assessment', score: 0.85, risk: 'medium', trend: 'up' },
  { opportunity: 'IT Help Desk Support', score: 0.78, risk: 'low', trend: 'stable' },
  { opportunity: 'Data Analytics Platform', score: 0.67, risk: 'medium', trend: 'down' },
  { opportunity: 'Environmental Remediation', score: 0.45, risk: 'high', trend: 'down' },
]

const riskDistribution = [
  { level: 'Low', count: 8, color: 'bg-emerald-500' },
  { level: 'Medium', count: 10, color: 'bg-aureon-500' },
  { level: 'High', count: 4, color: 'bg-rose-500' },
  { level: 'Critical', count: 2, color: 'bg-red-700' },
]

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-display font-bold text-slate-100 mb-2">
          Dashboard
        </h1>
        <p className="text-slate-400">
          Pipeline overview and performance metrics
        </p>
      </motion.div>

      {/* Pipeline Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {pipelineStats.map((stat, index) => (
          <div key={stat.label} className="card p-5">
            <div className="flex items-start justify-between mb-2">
              <span className="text-sm text-slate-400">{stat.label}</span>
              {stat.change !== 0 && (
                <span className={`flex items-center text-xs ${stat.change > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {stat.change > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  {Math.abs(stat.change)}
                </span>
              )}
            </div>
            <div className="text-3xl font-display font-bold text-slate-100 mb-1">
              {stat.value}
            </div>
            <div className="text-xs text-slate-500">{stat.period}</div>
          </div>
        ))}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Score Distribution */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <div className="flex items-center gap-2 mb-6">
            <Target className="w-5 h-5 text-aureon-400" />
            <h2 className="font-semibold text-slate-100">Score Distribution</h2>
          </div>
          
          <div className="flex justify-center mb-6">
            <ScoreRing score={0.72} size="lg" label="Pipeline Average" />
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Excellent (80-100%)</span>
              <span className="text-emerald-400 font-medium">8 opps</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Good (60-79%)</span>
              <span className="text-aureon-400 font-medium">10 opps</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Fair (40-59%)</span>
              <span className="text-amber-400 font-medium">4 opps</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Poor (&lt;40%)</span>
              <span className="text-rose-400 font-medium">2 opps</span>
            </div>
          </div>
        </motion.div>

        {/* Recent Scores */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6 lg:col-span-2"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-aureon-400" />
              <h2 className="font-semibold text-slate-100">Recent Scores</h2>
            </div>
            <button className="text-sm text-aureon-400 hover:text-aureon-300">
              View All
            </button>
          </div>

          <div className="space-y-3">
            {recentScores.map((item) => (
              <div
                key={item.opportunity}
                className="flex items-center gap-4 p-3 rounded-lg bg-cosmos-800/30 hover:bg-cosmos-800/50 transition-colors"
              >
                <ScoreRing score={item.score} size="sm" showLabel={false} />
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-slate-100 truncate">{item.opportunity}</h4>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={`text-xs ${
                      item.risk === 'low' ? 'text-emerald-400' :
                      item.risk === 'medium' ? 'text-aureon-400' :
                      'text-rose-400'
                    }`}>
                      {item.risk.charAt(0).toUpperCase() + item.risk.slice(1)} Risk
                    </span>
                  </div>
                </div>
                <div className={`flex items-center gap-1 text-sm ${
                  item.trend === 'up' ? 'text-emerald-400' :
                  item.trend === 'down' ? 'text-rose-400' :
                  'text-slate-400'
                }`}>
                  {item.trend === 'up' && <ArrowUpRight className="w-4 h-4" />}
                  {item.trend === 'down' && <ArrowDownRight className="w-4 h-4" />}
                  {item.trend === 'stable' && <span className="text-xs">—</span>}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Risk Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card p-6"
      >
        <div className="flex items-center gap-2 mb-6">
          <AlertTriangle className="w-5 h-5 text-aureon-400" />
          <h2 className="font-semibold text-slate-100">Risk Distribution</h2>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          {riskDistribution.map((item) => (
            <div key={item.level} className="bg-cosmos-800/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-3 h-3 rounded-full ${item.color}`} />
                <span className="text-sm text-slate-400">{item.level} Risk</span>
              </div>
              <div className="text-2xl font-bold text-slate-100">{item.count}</div>
              <div className="text-xs text-slate-500 mt-1">opportunities</div>
              <div className="mt-3 h-1.5 bg-cosmos-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${item.color} rounded-full transition-all duration-500`}
                  style={{ width: `${(item.count / 24) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Upcoming Deadlines */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card p-6"
      >
        <div className="flex items-center gap-2 mb-6">
          <Clock className="w-5 h-5 text-aureon-400" />
          <h2 className="font-semibold text-slate-100">Upcoming Deadlines</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-4">
            <div className="text-rose-400 text-sm font-medium mb-2">Due in 3 days</div>
            <h4 className="font-semibold text-slate-100 mb-1">Cloud Migration RFP</h4>
            <p className="text-xs text-slate-400">GSA Federal Acquisition Service</p>
          </div>
          <div className="bg-aureon-500/10 border border-aureon-500/20 rounded-xl p-4">
            <div className="text-aureon-400 text-sm font-medium mb-2">Due in 7 days</div>
            <h4 className="font-semibold text-slate-100 mb-1">Cybersecurity Services</h4>
            <p className="text-xs text-slate-400">Department of Defense</p>
          </div>
          <div className="bg-cosmos-500/10 border border-cosmos-500/20 rounded-xl p-4">
            <div className="text-cosmos-400 text-sm font-medium mb-2">Due in 14 days</div>
            <h4 className="font-semibold text-slate-100 mb-1">IT Support Services</h4>
            <p className="text-xs text-slate-400">Department of Veterans Affairs</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

