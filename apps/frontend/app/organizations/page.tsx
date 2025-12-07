'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Building2, Plus, Edit2, Trash2, MapPin, Users, DollarSign, Tag, RefreshCw, AlertCircle } from 'lucide-react'
import { api, Organization } from '@/lib/api'

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const fetchOrganizations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await api.listOrganizations()
      setOrganizations(data)
      if (data.length > 0 && !selectedOrg) {
        setSelectedOrg(data[0])
      }
    } catch (err) {
      console.error('Error fetching organizations:', err)
      setError('Unable to load organizations. Using sample data.')
      const mockData = getMockOrganizations()
      setOrganizations(mockData)
      setSelectedOrg(mockData[0])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOrganizations()
  }, [])

  const formatRevenue = (value?: number) => {
    if (!value) return 'N/A'
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`
    return `$${value}`
  }

  const handleCreateOrg = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    
    const newOrg = {
      name: formData.get('name') as string,
      naics_codes: (formData.get('naics_codes') as string).split(',').map(s => s.trim()).filter(Boolean),
      set_aside_types: (formData.get('set_aside_types') as string).split(',').map(s => s.trim()).filter(Boolean),
      city: formData.get('city') as string,
      state: formData.get('state') as string,
      capabilities_narrative: formData.get('capabilities') as string,
    }
    
    try {
      const created = await api.createOrganization(newOrg)
      setOrganizations([...organizations, created])
      setSelectedOrg(created)
      setShowCreateForm(false)
    } catch (err) {
      console.error('Error creating organization:', err)
      setError('Failed to create organization')
    }
  }

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
            Organizations
          </h1>
          <p className="text-slate-400">
            Manage organization profiles for opportunity matching
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchOrganizations} className="btn-secondary" disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={() => setShowCreateForm(true)} className="btn-primary">
            <Plus className="w-4 h-4" />
            Add Organization
          </button>
        </div>
      </motion.div>

      {/* Error Alert */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-amber-400" />
          <span className="text-amber-300">{error}</span>
        </motion.div>
      )}

      {/* Create Form Modal */}
      {showCreateForm && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
          onClick={() => setShowCreateForm(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="card p-6 max-w-lg w-full space-y-4"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-xl font-semibold text-slate-100">Create Organization</h2>
            <form onSubmit={handleCreateOrg} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Name *</label>
                <input name="name" required className="input" placeholder="Organization name" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">City</label>
                  <input name="city" className="input" placeholder="City" />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1">State</label>
                  <input name="state" className="input" placeholder="State" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">NAICS Codes</label>
                <input name="naics_codes" className="input" placeholder="541512, 541519" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Set-Aside Types</label>
                <input name="set_aside_types" className="input" placeholder="SB, SDVOSB, 8A" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Capabilities</label>
                <textarea name="capabilities" rows={3} className="input" placeholder="Describe your capabilities..." />
              </div>
              <div className="flex gap-3 justify-end">
                <button type="button" onClick={() => setShowCreateForm(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}

      {isLoading ? (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="card p-4 animate-pulse">
                <div className="h-6 bg-cosmos-700/50 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-cosmos-700/50 rounded w-1/2"></div>
              </div>
            ))}
          </div>
          <div className="lg:col-span-2">
            <div className="card p-6 animate-pulse">
              <div className="h-8 bg-cosmos-700/50 rounded w-1/2 mb-4"></div>
              <div className="h-4 bg-cosmos-700/50 rounded w-full mb-2"></div>
              <div className="h-4 bg-cosmos-700/50 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Organization List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1 space-y-4"
          >
            {organizations.length === 0 ? (
              <div className="card p-6 text-center">
                <Building2 className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                <p className="text-slate-400">No organizations yet</p>
                <button onClick={() => setShowCreateForm(true)} className="btn-primary mt-4">
                  <Plus className="w-4 h-4" />
                  Create First Organization
                </button>
              </div>
            ) : (
              organizations.map((org) => (
                <div
                  key={org.id}
                  onClick={() => setSelectedOrg(org)}
                  className={`card p-4 cursor-pointer transition-all ${
                    selectedOrg?.id === org.id
                      ? 'border-aureon-500/50 bg-aureon-500/5'
                      : 'hover:border-cosmos-700'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-cosmos-800 flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-aureon-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-slate-100 truncate">{org.name}</h3>
                      <p className="text-sm text-slate-500">
                        {[org.city, org.state].filter(Boolean).join(', ') || 'Location not set'}
                      </p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {(org.set_aside_types || []).slice(0, 2).map((type) => (
                          <span key={type} className="badge-gold text-xs">
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </motion.div>

          {/* Organization Details */}
          {selectedOrg && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="lg:col-span-2"
            >
              <div className="card p-6 space-y-6">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-display font-bold text-slate-100 mb-1">
                      {selectedOrg.name}
                    </h2>
                    {selectedOrg.legal_name && (
                      <p className="text-slate-400">{selectedOrg.legal_name}</p>
                    )}
                    {selectedOrg.uei && (
                      <p className="text-sm text-slate-500 font-mono mt-1">UEI: {selectedOrg.uei}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button className="btn-secondary p-2">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button className="btn-secondary p-2 text-rose-400 hover:bg-rose-500/10">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-cosmos-800/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-1">
                      <MapPin className="w-4 h-4" />
                      <span className="text-xs">Location</span>
                    </div>
                    <p className="font-semibold text-slate-100">
                      {[selectedOrg.city, selectedOrg.state].filter(Boolean).join(', ') || 'Not set'}
                    </p>
                  </div>
                  <div className="bg-cosmos-800/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-1">
                      <Users className="w-4 h-4" />
                      <span className="text-xs">Employees</span>
                    </div>
                    <p className="font-semibold text-slate-100">{selectedOrg.employee_count || 'N/A'}</p>
                  </div>
                  <div className="bg-cosmos-800/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-1">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-xs">Revenue</span>
                    </div>
                    <p className="font-semibold text-slate-100">{formatRevenue(selectedOrg.annual_revenue)}</p>
                  </div>
                  <div className="bg-cosmos-800/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-1">
                      <Tag className="w-4 h-4" />
                      <span className="text-xs">Set-Asides</span>
                    </div>
                    <p className="font-semibold text-slate-100">{(selectedOrg.set_aside_types || []).length}</p>
                  </div>
                </div>

                {/* NAICS Codes */}
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-3">NAICS Codes</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedOrg.naics_codes || []).length > 0 ? (
                      selectedOrg.naics_codes!.map((code) => (
                        <span key={code} className="badge-blue">
                          {code}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-sm">No NAICS codes set</span>
                    )}
                  </div>
                </div>

                {/* Set-Aside Types */}
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-3">Set-Aside Qualifications</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedOrg.set_aside_types || []).length > 0 ? (
                      selectedOrg.set_aside_types!.map((type) => (
                        <span key={type} className="badge-gold">
                          {type}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-sm">No set-aside qualifications set</span>
                    )}
                  </div>
                </div>

                {/* Capabilities */}
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-3">Capabilities Narrative</h3>
                  <p className="text-slate-300 leading-relaxed">
                    {selectedOrg.capabilities_narrative || 'No capabilities narrative set.'}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="pt-4 border-t border-cosmos-800/50 flex gap-4">
                  <button className="btn-primary">
                    Find Matching Opportunities
                  </button>
                  <button className="btn-secondary">
                    View Past Performance
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}

// Mock data fallback
function getMockOrganizations(): Organization[] {
  const now = new Date().toISOString()
  return [
    {
      id: '1',
      name: 'Acme Tech Solutions',
      legal_name: 'Acme Technology Solutions LLC',
      uei: 'ABCD12345678',
      naics_codes: ['541512', '541519', '541511'],
      psc_codes: ['D302', 'D306', 'D307'],
      set_aside_types: ['SB', 'SDVOSB'],
      city: 'Arlington',
      state: 'VA',
      employee_count: 45,
      annual_revenue: 8500000,
      capabilities_narrative: 'Full-stack software development, cloud migration, and cybersecurity services for federal agencies.',
      created_at: now,
      updated_at: now,
    },
    {
      id: '2',
      name: 'Delta Defense Systems',
      legal_name: 'Delta Defense Systems Inc',
      uei: 'EFGH87654321',
      naics_codes: ['336411', '541330', '541715'],
      psc_codes: ['1560', '1680', 'K039'],
      set_aside_types: ['SB', '8A'],
      city: 'San Diego',
      state: 'CA',
      employee_count: 120,
      annual_revenue: 25000000,
      capabilities_narrative: 'Defense systems integration, aerospace engineering, and R&D services.',
      created_at: now,
      updated_at: now,
    },
  ]
}
