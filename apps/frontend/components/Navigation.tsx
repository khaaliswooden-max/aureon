'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Home, 
  Search, 
  Building2, 
  BarChart3, 
  Settings,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'
import { clsx } from 'clsx'

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/opportunities', label: 'Opportunities', icon: Search },
  { href: '/organizations', label: 'Organizations', icon: Building2 },
  { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
]

export function Navigation() {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 bg-cosmos-950/80 backdrop-blur-xl border-b border-cosmos-800/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-aureon-400 to-aureon-600 flex items-center justify-center shadow-lg shadow-aureon-500/25 group-hover:shadow-aureon-500/40 transition-shadow">
                <span className="text-cosmos-950 font-display font-bold text-xl">A</span>
              </div>
              <div className="absolute -inset-1 rounded-xl bg-aureon-500/20 blur-lg opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="font-display font-bold text-xl text-slate-100 hidden sm:block">
              Aureon
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    'relative flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                    isActive
                      ? 'text-aureon-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-cosmos-800/50'
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="nav-indicator"
                      className="absolute inset-0 bg-aureon-500/10 border border-aureon-500/20 rounded-lg -z-10"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.5 }}
                    />
                  )}
                </Link>
              )
            })}
          </div>

          {/* Settings & Mobile Toggle */}
          <div className="flex items-center gap-2">
            <Link
              href="/settings"
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-cosmos-800/50 transition-colors"
            >
              <Settings className="w-5 h-5" />
            </Link>
            
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-cosmos-800/50 transition-colors"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden py-4 border-t border-cosmos-800/50"
          >
            <div className="flex flex-col gap-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={clsx(
                      'flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors',
                      isActive
                        ? 'text-aureon-400 bg-aureon-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-cosmos-800/50'
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  )
}

