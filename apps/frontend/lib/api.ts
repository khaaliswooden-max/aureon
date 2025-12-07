/**
 * API client for Aureon backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>
}

async function fetchAPI<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...fetchOptions } = options

  let url = `${API_BASE_URL}${endpoint}`
  
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }))
    throw new Error(error.message || `HTTP ${response.status}`)
  }

  return response.json()
}

// Types
export interface Organization {
  id: string
  name: string
  legal_name?: string
  uei?: string
  naics_codes?: string[]
  psc_codes?: string[]
  set_aside_types?: string[]
  city?: string
  state?: string
  employee_count?: number
  annual_revenue?: number
  capabilities_narrative?: string
  past_performance_summary?: string
  created_at: string
  updated_at: string
}

export interface Opportunity {
  id: string
  source_id: string
  source_system: string
  title: string
  description?: string
  notice_type?: string
  solicitation_number?: string
  naics_code?: string
  naics_description?: string
  psc_code?: string
  set_aside_type?: string
  response_deadline?: string
  posted_date?: string
  contract_type?: string
  estimated_value_min?: number
  estimated_value_max?: number
  place_of_performance_city?: string
  place_of_performance_state?: string
  contracting_office_name?: string
  status: string
  created_at: string
  updated_at: string
}

export interface RelevanceScore {
  id: string
  organization_id: string
  opportunity_id: string
  overall_score: number
  naics_score?: number
  semantic_score?: number
  geographic_score?: number
  size_score?: number
  past_performance_score?: number
  explanation?: string
  calculated_at: string
}

export interface RiskAssessment {
  id: string
  organization_id: string
  opportunity_id: string
  overall_risk_level: 'low' | 'medium' | 'high' | 'critical'
  overall_risk_score: number
  eligibility_risk: RiskCategory
  technical_risk: RiskCategory
  pricing_risk: RiskCategory
  resource_risk: RiskCategory
  compliance_risk: RiskCategory
  timeline_risk: RiskCategory
  risk_factors: string[]
  mitigation_suggestions: string[]
  assessed_at: string
}

interface RiskCategory {
  level: string
  score: number
  factors: string[]
}

export interface WinProbability {
  opportunity_id: string
  win_probability: number
  match_score: number
  factors: Record<string, number>
  recommendation: string
  confidence: number
  analysis: Record<string, string>
}

export interface SupplierVerification {
  supplier_id: string
  supplier_name: string
  verified: boolean
  section_889_status: string
  taa_status?: string
  overall_risk_score: number
  risk_level: string
  risk_factors: string[]
  recommendations: string[]
  verified_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// API functions
export const api = {
  // Health
  async getHealth() {
    return fetchAPI<{ status: string; version: string }>('/health')
  },

  // Organizations
  async listOrganizations(params?: { query?: string; page?: number; page_size?: number }) {
    return fetchAPI<Organization[]>('/organizations', { params })
  },

  async getOrganization(id: string) {
    return fetchAPI<Organization>(`/organizations/${id}`)
  },

  async createOrganization(data: Partial<Organization>) {
    return fetchAPI<Organization>('/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateOrganization(id: string, data: Partial<Organization>) {
    return fetchAPI<Organization>(`/organizations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  // Opportunities
  async listOpportunities(params?: {
    query?: string
    naics_code?: string
    set_aside_type?: string
    state?: string
    status?: string
    page?: number
    page_size?: number
    sort_by?: string
    sort_order?: string
  }) {
    return fetchAPI<PaginatedResponse<Opportunity>>('/opportunities', { params })
  },

  async getOpportunity(id: string) {
    return fetchAPI<Opportunity>(`/opportunities/${id}`)
  },

  async getOpportunityStats() {
    return fetchAPI<{
      total_active: number
      by_notice_type: Record<string, number>
      by_set_aside: Record<string, number>
    }>('/opportunities/stats/summary')
  },

  // Scoring
  async calculateRelevanceScore(organizationId: string, opportunityId: string) {
    return fetchAPI<RelevanceScore>('/scoring/calculate', {
      method: 'POST',
      body: JSON.stringify({ organization_id: organizationId, opportunity_id: opportunityId }),
    })
  },

  async getOrganizationScores(organizationId: string, minScore?: number) {
    return fetchAPI<{ items: RelevanceScore[]; organization_id: string }>(
      `/scoring/organization/${organizationId}`,
      { params: { min_score: minScore } }
    )
  },

  // Risk Assessment
  async assessRisk(organizationId: string, opportunityId: string) {
    return fetchAPI<RiskAssessment>('/risk/assess', {
      method: 'POST',
      body: JSON.stringify({ organization_id: organizationId, opportunity_id: opportunityId }),
    })
  },

  // Win Probability
  async calculateWinProbability(organizationId: string, opportunityId: string) {
    return fetchAPI<WinProbability>('/win-probability/calculate', {
      method: 'POST',
      body: JSON.stringify({ organization_id: organizationId, opportunity_id: opportunityId }),
    })
  },

  // Proposal Generation
  async generateProposalSection(
    organizationId: string,
    opportunityId: string,
    sectionType: string
  ) {
    return fetchAPI<{
      section_id: string
      title: string
      content: string
      word_count: number
      confidence: number
    }>('/proposals/generate-section', {
      method: 'POST',
      body: JSON.stringify({
        organization_id: organizationId,
        opportunity_id: opportunityId,
        section_type: sectionType,
      }),
    })
  },

  async generateFullProposal(organizationId: string, opportunityId: string, sections?: string[]) {
    return fetchAPI<{
      opportunity_id: string
      organization_id: string
      sections: Array<{
        section_id: string
        title: string
        content: string
        word_count: number
      }>
      executive_summary: string
      total_word_count: number
    }>('/proposals/generate', {
      method: 'POST',
      body: JSON.stringify({
        organization_id: organizationId,
        opportunity_id: opportunityId,
        sections,
      }),
    })
  },

  // Supply Chain Compliance
  async verifySupplier(
    supplierName: string,
    supplierId?: string,
    countryOfOrigin?: string
  ) {
    return fetchAPI<SupplierVerification>('/supply-chain/verify', {
      method: 'POST',
      body: JSON.stringify({
        supplier_name: supplierName,
        supplier_id: supplierId,
        country_of_origin: countryOfOrigin,
      }),
    })
  },

  async checkSection889(supplierName: string) {
    return fetchAPI<{
      supplier_name: string
      status: string
      prohibited_entities_matched: string[]
      risk_indicators: string[]
      recommendation: string
    }>('/supply-chain/section-889/check', {
      method: 'POST',
      body: JSON.stringify({ supplier_name: supplierName }),
    })
  },

  async checkTAACompliance(countryCode: string) {
    return fetchAPI<{
      country_code: string
      country_name: string
      status: string
      is_designated_country: boolean
      is_prohibited: boolean
      notes: string
    }>('/supply-chain/taa/check', {
      method: 'POST',
      body: JSON.stringify({ country_code: countryCode }),
    })
  },

  async getTAADesignatedCountries() {
    return fetchAPI<{
      designated_countries: Array<{ code: string; name: string }>
      total: number
    }>('/supply-chain/taa/designated-countries')
  },

  // Pricing Intelligence
  async getPricingRecommendation(opportunityId: string, laborMix?: Record<string, number>) {
    return fetchAPI<{
      opportunity_id: string
      recommended_price_min: number
      recommended_price_max: number
      competitive_position: string
      confidence: number
      notes: string[]
    }>('/pricing/recommendation', {
      method: 'POST',
      body: JSON.stringify({
        opportunity_id: opportunityId,
        labor_mix: laborMix,
      }),
    })
  },

  async calculateShouldCost(
    laborMix: Record<string, number>,
    durationMonths: number = 12,
    overheadRate: number = 1.5,
    profitMargin: number = 0.10
  ) {
    return fetchAPI<{
      labor_breakdown: Record<string, any>
      direct_labor: number
      overhead_cost: number
      profit: number
      total_price: number
    }>('/pricing/should-cost', {
      method: 'POST',
      body: JSON.stringify({
        labor_mix: laborMix,
        duration_months: durationMonths,
        overhead_rate: overheadRate,
        profit_margin: profitMargin,
      }),
    })
  },

  async getLaborRateBenchmarks(categories?: string) {
    return fetchAPI<Array<{
      labor_category: string
      min_rate: number
      max_rate: number
      median_rate: number
      sample_size: number
    }>>('/pricing/labor-rates', { params: { categories } })
  },

  // Ingestion
  async triggerIngestion(source: string, params?: Record<string, any>) {
    return fetchAPI<{ id: string; status: string }>('/ingestion/trigger', {
      method: 'POST',
      body: JSON.stringify({ source, params }),
    })
  },

  async getIngestionStatus(id: string) {
    return fetchAPI<{
      id: string
      source_system: string
      status: string
      records_fetched: number
      records_inserted: number
      records_updated: number
      records_failed: number
    }>(`/ingestion/status/${id}`)
  },

  async getIngestionHistory(limit: number = 20) {
    return fetchAPI<Array<{
      id: string
      source_system: string
      status: string
      started_at: string
      completed_at?: string
      records_fetched: number
    }>>('/ingestion/history', { params: { limit } })
  },

  // Authentication
  async login(email: string, password: string) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    return response.json()
  },

  async getCurrentUser(token: string) {
    return fetchAPI<{
      user_id: string
      email: string
      roles: string[]
      organization_id?: string
    }>('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async refreshToken(refreshToken: string) {
    return fetchAPI<{
      access_token: string
      token_type: string
      expires_in: number
    }>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  },
}

export default api
