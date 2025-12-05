'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Building2, Plus, Edit2, Trash2, MapPin, Users, DollarSign, Tag } from 'lucide-react'

// Mock organizations
const mockOrganizations = [
  {
    id: '1',
    name: 'Acme Tech Solutions',
    legalName: 'Acme Technology Solutions LLC',
    uei: 'ABCD12345678',
    naicsCodes: ['541512', '541519', '541511'],
    pscCodes: ['D302', 'D306', 'D307'],
    setAsideTypes: ['SB', 'SDVOSB'],
    city: 'Arlington',
    state: 'VA',
    employeeCount: 45,
    annualRevenue: 8500000,
    capabilitiesNarrative: 'Full-stack software development, cloud migration, and cybersecurity services for federal agencies.',
  },
  {
    id: '2',
    name: 'Delta Defense Systems',
    legalName: 'Delta Defense Systems Inc',
    uei: 'EFGH87654321',
    naicsCodes: ['336411', '541330', '541715'],
    pscCodes: ['1560', '1680', 'K039'],
    setAsideTypes: ['SB', '8A'],
    city: 'San Diego',
    state: 'CA',
    employeeCount: 120,
    annualRevenue: 25000000,
    capabilitiesNarrative: 'Defense systems integration, aerospace engineering, and R&D services.',
  },
]

export default function OrganizationsPage() {
  const [selectedOrg, setSelectedOrg] = useState(mockOrganizations[0])

  const formatRevenue = (value: number) => {
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`
    return `$${value}`
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
        <button className="btn-primary">
          <Plus className="w-4 h-4" />
          Add Organization
        </button>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Organization List */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1 space-y-4"
        >
          {mockOrganizations.map((org) => (
            <div
              key={org.id}
              onClick={() => setSelectedOrg(org)}
              className={`card p-4 cursor-pointer transition-all ${
                selectedOrg.id === org.id
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
                  <p className="text-sm text-slate-500">{org.city}, {org.state}</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {org.setAsideTypes.slice(0, 2).map((type) => (
                      <span key={type} className="badge-gold text-xs">
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Organization Details */}
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
                <p className="text-slate-400">{selectedOrg.legalName}</p>
                <p className="text-sm text-slate-500 font-mono mt-1">UEI: {selectedOrg.uei}</p>
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
                <p className="font-semibold text-slate-100">{selectedOrg.city}, {selectedOrg.state}</p>
              </div>
              <div className="bg-cosmos-800/30 rounded-xl p-4">
                <div className="flex items-center gap-2 text-slate-400 mb-1">
                  <Users className="w-4 h-4" />
                  <span className="text-xs">Employees</span>
                </div>
                <p className="font-semibold text-slate-100">{selectedOrg.employeeCount}</p>
              </div>
              <div className="bg-cosmos-800/30 rounded-xl p-4">
                <div className="flex items-center gap-2 text-slate-400 mb-1">
                  <DollarSign className="w-4 h-4" />
                  <span className="text-xs">Revenue</span>
                </div>
                <p className="font-semibold text-slate-100">{formatRevenue(selectedOrg.annualRevenue)}</p>
              </div>
              <div className="bg-cosmos-800/30 rounded-xl p-4">
                <div className="flex items-center gap-2 text-slate-400 mb-1">
                  <Tag className="w-4 h-4" />
                  <span className="text-xs">Set-Asides</span>
                </div>
                <p className="font-semibold text-slate-100">{selectedOrg.setAsideTypes.length}</p>
              </div>
            </div>

            {/* NAICS Codes */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">NAICS Codes</h3>
              <div className="flex flex-wrap gap-2">
                {selectedOrg.naicsCodes.map((code) => (
                  <span key={code} className="badge-blue">
                    {code}
                  </span>
                ))}
              </div>
            </div>

            {/* PSC Codes */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">PSC Codes</h3>
              <div className="flex flex-wrap gap-2">
                {selectedOrg.pscCodes.map((code) => (
                  <span key={code} className="badge bg-slate-700/50 text-slate-300 border border-slate-600/30">
                    {code}
                  </span>
                ))}
              </div>
            </div>

            {/* Set-Aside Types */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Set-Aside Qualifications</h3>
              <div className="flex flex-wrap gap-2">
                {selectedOrg.setAsideTypes.map((type) => (
                  <span key={type} className="badge-gold">
                    {type}
                  </span>
                ))}
              </div>
            </div>

            {/* Capabilities */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Capabilities Narrative</h3>
              <p className="text-slate-300 leading-relaxed">
                {selectedOrg.capabilitiesNarrative}
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
      </div>
    </div>
  )
}

