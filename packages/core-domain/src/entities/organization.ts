/**
 * Organization entity - represents a company or entity in the procurement ecosystem.
 */
import type { UUID, Address, Contact, AuditMetadata } from '../types/common'
import type { NAICSCode, PSCCode } from '../types/naics'
import type { SetAsideType } from '../types/set-asides'

/** Organization entity */
export interface Organization extends AuditMetadata {
  id: UUID
  
  // Identity
  name: string
  legalName?: string
  dba?: string // Doing Business As
  
  // Federal identifiers
  uei?: string           // Unique Entity Identifier (replaced DUNS)
  dunsNumber?: string    // Legacy DUNS (deprecated)
  cageCode?: string      // Commercial and Government Entity Code
  ein?: string           // Employer Identification Number
  
  // Classification
  naicsCodes: NAICSCode[]
  pscCodes: PSCCode[]
  setAsideTypes: SetAsideType[]
  
  // Location
  primaryAddress?: Address
  
  // Contacts
  primaryContact?: Contact
  contractsContact?: Contact
  
  // Size & capacity
  employeeCount?: number
  annualRevenue?: number // In USD cents
  foundedYear?: number
  
  // Capabilities
  capabilitiesNarrative?: string
  coreCompetencies?: string[]
  pastPerformanceSummary?: string
  
  // Certifications
  certifications?: Certification[]
  
  // Status
  status: OrganizationStatus
  samRegistrationStatus?: SAMRegistrationStatus
  samExpirationDate?: string
  
  // Metadata
  metadata?: Record<string, unknown>
}

/** Certification record */
export interface Certification {
  type: string
  name: string
  issuingAuthority: string
  issueDate: string
  expirationDate?: string
  status: 'active' | 'expired' | 'pending'
  verificationUrl?: string
}

/** Organization operational status */
export type OrganizationStatus = 
  | 'active'
  | 'inactive'
  | 'pending'
  | 'suspended'

/** SAM.gov registration status */
export type SAMRegistrationStatus =
  | 'active'
  | 'expired'
  | 'deactivated'
  | 'not_registered'

/** Create organization input */
export interface CreateOrganizationInput {
  name: string
  legalName?: string
  uei?: string
  naicsCodes?: NAICSCode[]
  pscCodes?: PSCCode[]
  setAsideTypes?: SetAsideType[]
  primaryAddress?: Address
  employeeCount?: number
  annualRevenue?: number
  capabilitiesNarrative?: string
}

/** Update organization input */
export interface UpdateOrganizationInput {
  name?: string
  legalName?: string
  naicsCodes?: NAICSCode[]
  pscCodes?: PSCCode[]
  setAsideTypes?: SetAsideType[]
  primaryAddress?: Address
  employeeCount?: number
  annualRevenue?: number
  capabilitiesNarrative?: string
  coreCompetencies?: string[]
  pastPerformanceSummary?: string
}

/** Organization search criteria */
export interface OrganizationSearchCriteria {
  query?: string
  naicsCodes?: NAICSCode[]
  setAsideTypes?: SetAsideType[]
  states?: string[]
  minEmployees?: number
  maxEmployees?: number
  status?: OrganizationStatus
}

