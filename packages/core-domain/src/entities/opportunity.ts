/**
 * Opportunity entity - represents a procurement opportunity.
 */
import type { UUID, Address, Contact, AuditMetadata, ISODateTime, MonetaryRange, SourceIdentifier } from '../types/common'
import type { NAICSCode, PSCCode } from '../types/naics'
import type { SetAsideType } from '../types/set-asides'

/** Procurement opportunity entity */
export interface Opportunity extends AuditMetadata {
  id: UUID
  
  // Source tracking
  source: SourceIdentifier
  
  // Basic information
  title: string
  description?: string
  noticeType: NoticeType
  solicitationNumber?: string
  
  // Classification
  naicsCode?: NAICSCode
  naicsDescription?: string
  pscCode?: PSCCode
  pscDescription?: string
  setAsideType?: SetAsideType
  
  // Timeline
  postedDate?: ISODateTime
  responseDeadline?: ISODateTime
  archiveDate?: ISODateTime
  performancePeriodStart?: ISODateTime
  performancePeriodEnd?: ISODateTime
  
  // Contract details
  contractType?: ContractType
  estimatedValue?: MonetaryRange
  baseYears?: number
  optionYears?: number
  
  // Place of performance
  placeOfPerformance?: Address
  
  // Contracting office
  contractingOffice: ContractingOffice
  
  // Points of contact
  primaryContact?: Contact
  secondaryContact?: Contact
  
  // Award information (if awarded)
  awardInfo?: AwardInfo
  
  // Status
  status: OpportunityStatus
  
  // Attachments & amendments
  attachments?: Attachment[]
  amendments?: Amendment[]
  
  // Requirements
  securityClearanceRequired?: string
  requiresCertifications?: string[]
  
  // Raw data for audit
  rawData?: Record<string, unknown>
  ingestedAt: ISODateTime
}

/** Notice type classification */
export type NoticeType =
  | 'presolicitation'
  | 'solicitation'
  | 'combined_synopsis'
  | 'sources_sought'
  | 'special_notice'
  | 'award_notice'
  | 'justification'
  | 'intent_to_bundle'
  | 'sale_of_surplus'
  | 'modification'
  | 'cancellation'
  | 'other'

/** Contract type */
export type ContractType =
  | 'firm_fixed_price'
  | 'time_and_materials'
  | 'labor_hour'
  | 'cost_plus_fixed_fee'
  | 'cost_plus_award_fee'
  | 'cost_plus_incentive_fee'
  | 'fixed_price_incentive'
  | 'idiq'
  | 'bpa'
  | 'other'

/** Opportunity lifecycle status */
export type OpportunityStatus =
  | 'forecast'
  | 'presolicitation'
  | 'active'
  | 'closed'
  | 'awarded'
  | 'cancelled'
  | 'archived'

/** Contracting office information */
export interface ContractingOffice {
  name?: string
  address?: Address
  agencyCode?: string
  agencyName?: string
  departmentCode?: string
  departmentName?: string
}

/** Award information */
export interface AwardInfo {
  awardDate: ISODateTime
  awardAmount?: number
  awardee: {
    name: string
    uei?: string
    address?: Address
  }
  contractNumber?: string
}

/** Attachment reference */
export interface Attachment {
  name: string
  url: string
  type?: string
  size?: number
  addedDate?: ISODateTime
}

/** Solicitation amendment */
export interface Amendment {
  number: string
  description?: string
  date: ISODateTime
  url?: string
}

/** Opportunity search criteria */
export interface OpportunitySearchCriteria {
  query?: string
  naicsCodes?: NAICSCode[]
  pscCodes?: PSCCode[]
  setAsideTypes?: SetAsideType[]
  noticeTypes?: NoticeType[]
  states?: string[]
  agencies?: string[]
  postedAfter?: ISODateTime
  postedBefore?: ISODateTime
  deadlineAfter?: ISODateTime
  deadlineBefore?: ISODateTime
  minValue?: number
  maxValue?: number
  status?: OpportunityStatus[]
}

