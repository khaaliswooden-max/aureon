'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, SlidersHorizontal, RefreshCw } from 'lucide-react'
import { OpportunityCard } from '@/components/OpportunityCard'

// Mock data for demonstration
const mockOpportunities = [
  {
    id: '1',
    title: 'Cloud Migration Services for Federal Data Centers',
    description: 'Professional services for migrating legacy on-premises infrastructure to AWS GovCloud and Azure Government environments.',
    naicsCode: '541512',
    naicsDescription: 'Computer Systems Design Services',
    setAsideType: 'Small Business',
    contractingOfficeName: 'GSA Federal Acquisition Service',
    placeOfPerformanceCity: 'Washington',
    placeOfPerformanceState: 'DC',
    responseDeadline: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 500000,
    estimatedValueMax: 2000000,
    relevanceScore: 0.92,
  },
  {
    id: '2',
    title: 'Cybersecurity Assessment and Continuous Monitoring',
    description: 'Comprehensive security services including vulnerability assessments, penetration testing, and 24/7 SOC monitoring.',
    naicsCode: '541519',
    naicsDescription: 'Other Computer Related Services',
    setAsideType: '8(a)',
    contractingOfficeName: 'Department of Defense - DISA',
    placeOfPerformanceCity: 'Arlington',
    placeOfPerformanceState: 'VA',
    responseDeadline: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 1000000,
    estimatedValueMax: 5000000,
    relevanceScore: 0.85,
  },
  {
    id: '3',
    title: 'Environmental Remediation - Former Military Base',
    description: 'Complete site assessment, remediation planning, and cleanup services for contaminated soil and groundwater.',
    naicsCode: '562910',
    naicsDescription: 'Remediation Services',
    setAsideType: 'WOSB',
    contractingOfficeName: 'US Army Corps of Engineers',
    placeOfPerformanceCity: 'Denver',
    placeOfPerformanceState: 'CO',
    responseDeadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 3000000,
    estimatedValueMax: 8000000,
    relevanceScore: 0.67,
  },
  {
    id: '4',
    title: 'IT Help Desk Support Services',
    description: 'Tier 1-3 technical support for end-user computing, including hardware, software, and network troubleshooting.',
    naicsCode: '541513',
    naicsDescription: 'Computer Facilities Management Services',
    setAsideType: 'SDVOSB',
    contractingOfficeName: 'Department of Veterans Affairs',
    placeOfPerformanceCity: 'Multiple Locations',
    placeOfPerformanceState: 'US',
    responseDeadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 200000,
    estimatedValueMax: 750000,
    relevanceScore: 0.78,
  },
  {
    id: '5',
    title: 'Data Analytics Platform Development',
    description: 'Design and implementation of enterprise data analytics solution including data warehouse, ETL pipelines, and visualization dashboards.',
    naicsCode: '541511',
    naicsDescription: 'Custom Computer Programming Services',
    setAsideType: 'Small Business',
    contractingOfficeName: 'Department of Commerce',
    placeOfPerformanceCity: 'Suitland',
    placeOfPerformanceState: 'MD',
    responseDeadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 1500000,
    estimatedValueMax: 4000000,
    relevanceScore: 0.88,
  },
  {
    id: '6',
    title: 'Training and Professional Development Services',
    description: 'Leadership development, technical training, and organizational change management consulting services.',
    naicsCode: '611430',
    naicsDescription: 'Professional and Management Development Training',
    setAsideType: 'HUBZone',
    contractingOfficeName: 'Office of Personnel Management',
    placeOfPerformanceCity: 'Washington',
    placeOfPerformanceState: 'DC',
    responseDeadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
    postedDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedValueMin: 100000,
    estimatedValueMax: 500000,
    relevanceScore: 0.45,
  },
]

export default function OpportunitiesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const filteredOpportunities = mockOpportunities.filter(
    (opp) =>
      opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      opp.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      opp.naicsCode?.includes(searchQuery)
  )

  const handleRefresh = () => {
    setIsLoading(true)
    setTimeout(() => setIsLoading(false), 1000)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-display font-bold text-slate-100 mb-2">
          Opportunities
        </h1>
        <p className="text-slate-400">
          Discover and analyze procurement opportunities matched to your profile
        </p>
      </motion.div>

      {/* Search & Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-4"
      >
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search Input */}
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="text"
              placeholder="Search by keyword, NAICS code, or agency..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-12"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-2">
            <button className="btn-secondary">
              <Filter className="w-4 h-4" />
              <span className="hidden sm:inline">Filters</span>
            </button>
            <button className="btn-secondary">
              <SlidersHorizontal className="w-4 h-4" />
              <span className="hidden sm:inline">Sort</span>
            </button>
            <button
              onClick={handleRefresh}
              className="btn-secondary"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Active Filters */}
        <div className="flex flex-wrap gap-2 mt-4">
          <span className="badge-gold">
            Set-Aside: Small Business ✕
          </span>
          <span className="badge-blue">
            NAICS: 541512 ✕
          </span>
          <span className="badge-green">
            Score &gt; 60% ✕
          </span>
        </div>
      </motion.div>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-400">
            Showing <span className="text-slate-200 font-medium">{filteredOpportunities.length}</span> opportunities
          </p>
          <p className="text-sm text-slate-500">
            Sorted by relevance score
          </p>
        </div>

        <div className="grid gap-4">
          {filteredOpportunities.map((opportunity, index) => (
            <motion.div
              key={opportunity.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
            >
              <OpportunityCard {...opportunity} />
            </motion.div>
          ))}
        </div>
      </div>

      {/* Pagination placeholder */}
      <div className="flex justify-center">
        <div className="flex items-center gap-2">
          <button className="btn-secondary px-4 py-2" disabled>
            Previous
          </button>
          <span className="px-4 py-2 text-slate-400">Page 1 of 1</span>
          <button className="btn-secondary px-4 py-2" disabled>
            Next
          </button>
        </div>
      </div>
    </div>
  )
}

