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
  legalName?: string
  uei?: string
  naicsCodes?: string[]
  pscCodes?: string[]
  setAsideTypes?: string[]
  city?: string
  state?: string
  employeeCount?: number
  annualRevenue?: number
  capabilitiesNarrative?: string
  createdAt: string
  updatedAt: string
}

export interface Opportunity {
  id: string
  sourceId: string
  sourceSystem: string
  title: string
  description?: string
  noticeType?: string
  solicitationNumber?: string
  naicsCode?: string
  naicsDescription?: string
  pscCode?: string
  setAsideType?: string
  responseDeadline?: string
  postedDate?: string
  contractType?: string
  estimatedValueMin?: number
  estimatedValueMax?: number
  placeOfPerformanceCity?: string
  placeOfPerformanceState?: string
  contractingOfficeName?: string
  status: string
  createdAt: string
  updatedAt: string
}

export interface RelevanceScore {
  id: string
  organizationId: string
  opportunityId: string
  overallScore: number
  naicsScore?: number
  semanticScore?: number
  geographicScore?: number
  sizeScore?: number
  pastPerformanceScore?: number
  explanation?: string
  calculatedAt: string
}

export interface RiskAssessment {
  id: string
  organizationId: string
  opportunityId: string
  overallRiskLevel: 'low' | 'medium' | 'high' | 'critical'
  overallRiskScore: number
  eligibilityRisk: RiskCategory
  technicalRisk: RiskCategory
  pricingRisk: RiskCategory
  resourceRisk: RiskCategory
  complianceRisk: RiskCategory
  timelineRisk: RiskCategory
  riskFactors: string[]
  mitigationSuggestions: string[]
  assessedAt: string
}

interface RiskCategory {
  level: string
  score: number
  factors: string[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  pages: number
}

// API functions
export const api = {
  // Health
  async getHealth() {
    return fetchAPI<{ status: string; version: string }>('/health')
  },

  // Organizations
  async listOrganizations(params?: { query?: string; page?: number; pageSize?: number }) {
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
    naicsCode?: string
    setAsideType?: string
    state?: string
    status?: string
    page?: number
    pageSize?: number
    sortBy?: string
    sortOrder?: string
  }) {
    return fetchAPI<PaginatedResponse<Opportunity>>('/opportunities', { params })
  },

  async getOpportunity(id: string) {
    return fetchAPI<Opportunity>(`/opportunities/${id}`)
  },

  // Scoring
  async calculateRelevanceScore(organizationId: string, opportunityId: string) {
    return fetchAPI<RelevanceScore>('/scoring/calculate', {
      method: 'POST',
      body: JSON.stringify({ organization_id: organizationId, opportunity_id: opportunityId }),
    })
  },

  async getOrganizationScores(organizationId: string, minScore?: number) {
    return fetchAPI<{ items: RelevanceScore[]; organizationId: string }>(
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

  async getOrganizationRiskSummary(organizationId: string) {
    return fetchAPI<{
      organizationId: string
      totalAssessed: number
      byRiskLevel: Record<string, number>
      averageRiskScore: number
    }>(`/risk/organization/${organizationId}/summary`)
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
      sourceSystem: string
      status: string
      recordsFetched: number
      recordsInserted: number
      recordsUpdated: number
      recordsFailed: number
    }>(`/ingestion/status/${id}`)
  },
}

export default api

