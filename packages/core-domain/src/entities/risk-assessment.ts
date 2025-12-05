/**
 * Risk Assessment entity - comprehensive bid/no-bid risk analysis.
 */
import type { UUID, ISODateTime, Percentage } from '../types/common'

/** Risk assessment entity */
export interface RiskAssessment {
  id: UUID
  organizationId: UUID
  opportunityId: UUID
  
  // Overall assessment
  overallRiskLevel: RiskLevel
  overallRiskScore: Percentage // 0.0 = no risk, 1.0 = maximum risk
  
  // Category assessments
  eligibilityRisk: RiskCategory
  technicalRisk: RiskCategory
  pricingRisk: RiskCategory
  resourceRisk: RiskCategory
  complianceRisk: RiskCategory
  timelineRisk: RiskCategory
  
  // Aggregated factors
  riskFactors: string[]
  mitigationSuggestions: string[]
  
  // Metadata
  assessedAt: ISODateTime
  modelVersion: string
}

/** Risk level classification */
export type RiskLevel =
  | 'low'       // 0.00 - 0.25
  | 'medium'    // 0.26 - 0.50
  | 'high'      // 0.51 - 0.75
  | 'critical'  // 0.76 - 1.00

/** Individual risk category assessment */
export interface RiskCategory {
  level: RiskLevel
  score: Percentage
  factors: string[]
}

/** Get risk level from score */
export function getRiskLevel(score: Percentage): RiskLevel {
  if (score <= 0.25) return 'low'
  if (score <= 0.50) return 'medium'
  if (score <= 0.75) return 'high'
  return 'critical'
}

/** Risk category weights for overall calculation */
export interface RiskWeights {
  eligibility: number
  technical: number
  pricing: number
  resource: number
  compliance: number
  timeline: number
}

/** Default risk weights */
export const DEFAULT_RISK_WEIGHTS: RiskWeights = {
  eligibility: 0.25,
  technical: 0.20,
  pricing: 0.15,
  resource: 0.15,
  compliance: 0.15,
  timeline: 0.10,
}

/** Risk assessment request */
export interface AssessRiskRequest {
  organizationId: UUID
  opportunityId: UUID
  weights?: Partial<RiskWeights>
}

/** Bid/No-Bid recommendation */
export interface BidRecommendation {
  recommendation: 'bid' | 'no_bid' | 'conditional_bid' | 'review_required'
  confidence: Percentage
  reasoning: string[]
  conditions?: string[] // For conditional_bid
}

/** Generate bid recommendation based on scores */
export function generateBidRecommendation(
  relevanceScore: Percentage,
  riskScore: Percentage
): BidRecommendation {
  // High relevance + low risk = bid
  if (relevanceScore >= 0.7 && riskScore <= 0.3) {
    return {
      recommendation: 'bid',
      confidence: 0.9,
      reasoning: [
        'Strong alignment with organization capabilities',
        'Manageable risk profile',
        'Good probability of competitive success'
      ]
    }
  }
  
  // High relevance + medium risk = conditional bid
  if (relevanceScore >= 0.6 && riskScore <= 0.5) {
    return {
      recommendation: 'conditional_bid',
      confidence: 0.7,
      reasoning: [
        'Good capability alignment',
        'Some risk factors require attention'
      ],
      conditions: [
        'Address identified risk factors before commitment',
        'Consider teaming for capability gaps',
        'Ensure adequate resources available'
      ]
    }
  }
  
  // Low relevance or high risk = no bid
  if (relevanceScore < 0.4 || riskScore > 0.7) {
    return {
      recommendation: 'no_bid',
      confidence: 0.85,
      reasoning: relevanceScore < 0.4
        ? ['Poor alignment with core capabilities', 'Low probability of success']
        : ['Risk level exceeds acceptable threshold', 'Significant barriers to success']
    }
  }
  
  // Everything else = review required
  return {
    recommendation: 'review_required',
    confidence: 0.5,
    reasoning: [
      'Mixed signals in analysis',
      'Manual review recommended before decision',
      'Consider strategic value beyond immediate metrics'
    ]
  }
}

