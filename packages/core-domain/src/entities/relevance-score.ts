/**
 * Relevance Score entity - measures alignment between organization and opportunity.
 */
import type { UUID, ISODateTime, Percentage } from '../types/common'

/** Relevance score entity */
export interface RelevanceScore {
  id: UUID
  organizationId: UUID
  opportunityId: UUID
  
  // Overall score
  overallScore: Percentage // 0.0 to 1.0
  
  // Component scores
  naicsScore?: Percentage
  semanticScore?: Percentage
  geographicScore?: Percentage
  sizeScore?: Percentage
  pastPerformanceScore?: Percentage
  competitionScore?: Percentage
  
  // Weights used
  componentWeights: RelevanceWeights
  
  // Explanation
  explanation?: string
  
  // Metadata
  calculatedAt: ISODateTime
  modelVersion: string
}

/** Weights for relevance score components */
export interface RelevanceWeights {
  naics: number
  semantic: number
  geographic: number
  size: number
  pastPerformance: number
  competition?: number
}

/** Default relevance weights */
export const DEFAULT_RELEVANCE_WEIGHTS: RelevanceWeights = {
  naics: 0.25,
  semantic: 0.30,
  geographic: 0.15,
  size: 0.15,
  pastPerformance: 0.15,
}

/** Relevance score tier */
export type RelevanceTier = 
  | 'excellent'   // 0.80 - 1.00
  | 'good'        // 0.60 - 0.79
  | 'fair'        // 0.40 - 0.59
  | 'poor'        // 0.00 - 0.39

/** Get tier from score */
export function getRelevanceTier(score: Percentage): RelevanceTier {
  if (score >= 0.80) return 'excellent'
  if (score >= 0.60) return 'good'
  if (score >= 0.40) return 'fair'
  return 'poor'
}

/** Relevance score calculation request */
export interface CalculateRelevanceRequest {
  organizationId: UUID
  opportunityId: UUID
  weights?: Partial<RelevanceWeights>
}

/** Batch relevance calculation request */
export interface BatchRelevanceRequest {
  organizationId: UUID
  opportunityIds: UUID[]
  weights?: Partial<RelevanceWeights>
}

/** Relevance score with opportunity details for display */
export interface ScoredOpportunity {
  opportunityId: UUID
  opportunityTitle: string
  score: RelevanceScore
  tier: RelevanceTier
}

