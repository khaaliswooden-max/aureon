'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, SlidersHorizontal, RefreshCw, AlertCircle } from 'lucide-react'
import { OpportunityCard } from '@/components/OpportunityCard'
import { api, Opportunity } from '@/lib/api'

export default function OpportunitiesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  // Filters
  const [naicsFilter, setNaicsFilter] = useState('')
  const [setAsideFilter, setSetAsideFilter] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  const fetchOpportunities = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await api.listOpportunities({
        query: searchQuery || undefined,
        naics_code: naicsFilter || undefined,
        set_aside_type: setAsideFilter || undefined,
        page,
        page_size: 20,
        sort_by: 'posted_date',
        sort_order: 'desc',
      })
      
      setOpportunities(response.items)
      setTotalPages(response.pages)
      setTotal(response.total)
    } catch (err) {
      console.error('Error fetching opportunities:', err)
      setError('Failed to load opportunities. Make sure the backend is running.')
      // Use mock data as fallback
      setOpportunities(getMockOpportunities())
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOpportunities()
  }, [page])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchOpportunities()
  }

  const handleRefresh = () => {
    fetchOpportunities()
  }

  const clearFilters = () => {
    setSearchQuery('')
    setNaicsFilter('')
    setSetAsideFilter('')
    setPage(1)
    fetchOpportunities()
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

      {/* Error Alert */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-4 flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-rose-400" />
          <span className="text-rose-300">{error}</span>
        </motion.div>
      )}

      {/* Search & Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-4"
      >
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
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
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-secondary ${showFilters ? 'ring-2 ring-aureon-500/50' : ''}`}
            >
              <Filter className="w-4 h-4" />
              <span className="hidden sm:inline">Filters</span>
            </button>
            <button type="submit" className="btn-primary">
              Search
            </button>
            <button
              type="button"
              onClick={handleRefresh}
              className="btn-secondary"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </form>

        {/* Expanded Filters */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 pt-4 border-t border-cosmos-700/50 grid md:grid-cols-3 gap-4"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-2">NAICS Code</label>
              <input
                type="text"
                placeholder="e.g., 541512"
                value={naicsFilter}
                onChange={(e) => setNaicsFilter(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-2">Set-Aside</label>
              <select
                value={setAsideFilter}
                onChange={(e) => setSetAsideFilter(e.target.value)}
                className="input"
              >
                <option value="">All Set-Asides</option>
                <option value="Small Business">Small Business</option>
                <option value="8(a)">8(a)</option>
                <option value="SDVOSB">SDVOSB</option>
                <option value="WOSB">WOSB</option>
                <option value="HUBZone">HUBZone</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                type="button"
                onClick={clearFilters}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </motion.div>
        )}

        {/* Active Filters */}
        {(naicsFilter || setAsideFilter) && (
          <div className="flex flex-wrap gap-2 mt-4">
            {naicsFilter && (
              <span className="badge-blue">
                NAICS: {naicsFilter}
                <button onClick={() => setNaicsFilter('')} className="ml-1">✕</button>
              </span>
            )}
            {setAsideFilter && (
              <span className="badge-gold">
                Set-Aside: {setAsideFilter}
                <button onClick={() => setSetAsideFilter('')} className="ml-1">✕</button>
              </span>
            )}
          </div>
        )}
      </motion.div>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-400">
            {isLoading ? (
              'Loading...'
            ) : (
              <>
                Showing <span className="text-slate-200 font-medium">{opportunities.length}</span> of{' '}
                <span className="text-slate-200 font-medium">{total}</span> opportunities
              </>
            )}
          </p>
          <p className="text-sm text-slate-500">
            Sorted by posted date
          </p>
        </div>

        {isLoading ? (
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-6 bg-cosmos-700/50 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-cosmos-700/50 rounded w-full mb-2"></div>
                <div className="h-4 bg-cosmos-700/50 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-4">
            {opportunities.map((opportunity, index) => (
              <motion.div
                key={opportunity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 + index * 0.03 }}
              >
                <OpportunityCard
                  id={opportunity.id}
                  title={opportunity.title}
                  description={opportunity.description}
                  naicsCode={opportunity.naics_code}
                  naicsDescription={opportunity.naics_description}
                  setAsideType={opportunity.set_aside_type}
                  contractingOfficeName={opportunity.contracting_office_name}
                  placeOfPerformanceCity={opportunity.place_of_performance_city}
                  placeOfPerformanceState={opportunity.place_of_performance_state}
                  responseDeadline={opportunity.response_deadline}
                  postedDate={opportunity.posted_date}
                  estimatedValueMin={opportunity.estimated_value_min}
                  estimatedValueMax={opportunity.estimated_value_max}
                />
              </motion.div>
            ))}
          </div>
        )}

        {opportunities.length === 0 && !isLoading && (
          <div className="card p-12 text-center">
            <p className="text-slate-400">No opportunities found matching your criteria.</p>
            <button onClick={clearFilters} className="btn-secondary mt-4">
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn-secondary px-4 py-2 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-slate-400">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="btn-secondary px-4 py-2 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Mock data for fallback when API is unavailable
function getMockOpportunities(): Opportunity[] {
  const now = new Date()
  return [
    {
      id: '1',
      source_id: 'SAMPLE-001',
      source_system: 'sam.gov',
      title: 'Cloud Migration Services for Federal Data Centers',
      description: 'Professional services for migrating legacy on-premises infrastructure to AWS GovCloud and Azure Government environments.',
      naics_code: '541512',
      naics_description: 'Computer Systems Design Services',
      set_aside_type: 'Small Business',
      contracting_office_name: 'GSA Federal Acquisition Service',
      place_of_performance_city: 'Washington',
      place_of_performance_state: 'DC',
      response_deadline: new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000).toISOString(),
      posted_date: new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_value_min: 500000,
      estimated_value_max: 2000000,
      status: 'active',
      created_at: now.toISOString(),
      updated_at: now.toISOString(),
    },
    {
      id: '2',
      source_id: 'SAMPLE-002',
      source_system: 'sam.gov',
      title: 'Cybersecurity Assessment and Continuous Monitoring',
      description: 'Comprehensive security services including vulnerability assessments, penetration testing, and 24/7 SOC monitoring.',
      naics_code: '541519',
      naics_description: 'Other Computer Related Services',
      set_aside_type: '8(a)',
      contracting_office_name: 'Department of Defense - DISA',
      place_of_performance_city: 'Arlington',
      place_of_performance_state: 'VA',
      response_deadline: new Date(now.getTime() + 21 * 24 * 60 * 60 * 1000).toISOString(),
      posted_date: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_value_min: 1000000,
      estimated_value_max: 5000000,
      status: 'active',
      created_at: now.toISOString(),
      updated_at: now.toISOString(),
    },
    {
      id: '3',
      source_id: 'SAMPLE-003',
      source_system: 'sam.gov',
      title: 'Environmental Remediation - Former Military Base',
      description: 'Complete site assessment, remediation planning, and cleanup services for contaminated soil and groundwater.',
      naics_code: '562910',
      naics_description: 'Remediation Services',
      set_aside_type: 'WOSB',
      contracting_office_name: 'US Army Corps of Engineers',
      place_of_performance_city: 'Denver',
      place_of_performance_state: 'CO',
      response_deadline: new Date(now.getTime() + 45 * 24 * 60 * 60 * 1000).toISOString(),
      posted_date: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      estimated_value_min: 3000000,
      estimated_value_max: 8000000,
      status: 'active',
      created_at: now.toISOString(),
      updated_at: now.toISOString(),
    },
  ]
}
