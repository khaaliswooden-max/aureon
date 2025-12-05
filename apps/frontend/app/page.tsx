'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Sparkles, Target, Shield, Globe2 } from 'lucide-react'
import Link from 'next/link'
import { StatsCard } from '@/components/StatsCard'
import { FeatureCard } from '@/components/FeatureCard'

const features = [
  {
    icon: Target,
    title: 'Relevance Scoring',
    description: 'AI-powered matching finds opportunities aligned with your capabilities, NAICS codes, and past performance.',
    color: 'aureon' as const,
  },
  {
    icon: Shield,
    title: 'Risk Assessment',
    description: 'Comprehensive bid/no-bid analysis covering eligibility, technical, pricing, and compliance risks.',
    color: 'emerald' as const,
  },
  {
    icon: Globe2,
    title: 'Multi-Jurisdiction',
    description: 'Unified access to federal, state, and commercial procurement across 50+ regimes.',
    color: 'cosmos' as const,
  },
]

const stats = [
  { label: 'Active Opportunities', value: '12,450+', change: '+340 today' },
  { label: 'Avg. Relevance Score', value: '78%', change: '+5% vs baseline' },
  { label: 'Time Saved', value: '4.2 hrs', change: 'per opportunity' },
  { label: 'Risk Detection', value: '94%', change: 'accuracy rate' },
]

export default function HomePage() {
  return (
    <div className="space-y-24">
      {/* Hero Section */}
      <section className="relative pt-16 pb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-aureon-500/10 border border-aureon-500/20 text-aureon-400 text-sm font-medium mb-8"
          >
            <Sparkles className="w-4 h-4" />
            <span>Planetary Procurement Substrate v0.1</span>
          </motion.div>

          <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight mb-6">
            <span className="text-gradient">Intelligent</span>{' '}
            <span className="text-slate-100">Procurement</span>
            <br />
            <span className="text-slate-400">Everywhere</span>
          </h1>

          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Aureon unifies fragmented procurement data into a single intelligent substrate,
            enabling smarter opportunity discovery, scoring, and risk assessment at planetary scale.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/opportunities" className="btn-primary">
              <span>Explore Opportunities</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/organizations" className="btn-secondary">
              Configure Your Profile
            </Link>
          </div>
        </motion.div>

        {/* Floating orb decoration */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none">
          <div className="absolute inset-0 rounded-full bg-gradient-radial from-aureon-500/10 via-cosmos-500/5 to-transparent blur-3xl animate-float" />
        </div>
      </section>

      {/* Stats Section */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <StatsCard {...stat} />
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Features Section */}
      <section>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="section-title text-3xl mb-3">Core Capabilities</h2>
          <p className="section-subtitle text-lg max-w-2xl mx-auto">
            From discovery to decision—every step powered by intelligence
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
            >
              <FeatureCard {...feature} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="card p-12 text-center relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-aureon-500/10 via-transparent to-cosmos-500/10" />
          <div className="relative z-10">
            <h2 className="text-3xl font-display font-bold mb-4">
              Ready to transform your procurement?
            </h2>
            <p className="text-slate-400 mb-8 max-w-xl mx-auto">
              Join organizations using Aureon to discover better opportunities,
              make faster decisions, and win more contracts.
            </p>
            <Link href="/opportunities" className="btn-primary">
              Get Started Free
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  )
}

