/**
 * Validation utilities for domain entities.
 */

import type { NAICSCode, PSCCode } from '../types/naics'
import type { SetAsideType } from '../types/set-asides'

/** UEI validation - 12 alphanumeric characters */
export function isValidUEI(uei: string): boolean {
  return /^[A-Z0-9]{12}$/.test(uei.toUpperCase())
}

/** DUNS validation - 9 digits (deprecated but may exist in legacy data) */
export function isValidDUNS(duns: string): boolean {
  return /^\d{9}$/.test(duns)
}

/** CAGE Code validation - 5 alphanumeric characters */
export function isValidCAGECode(cage: string): boolean {
  return /^[A-Z0-9]{5}$/.test(cage.toUpperCase())
}

/** NAICS code validation - 2-6 digits */
export function isValidNAICSCode(code: NAICSCode): boolean {
  return /^\d{2,6}$/.test(code)
}

/** PSC code validation - variable format */
export function isValidPSCCode(code: PSCCode): boolean {
  // PSC codes can be letters followed by numbers, or just letters/numbers
  return /^[A-Z0-9]{1,8}$/.test(code.toUpperCase())
}

/** Email validation */
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/** Phone validation (US format) */
export function isValidUSPhone(phone: string): boolean {
  const cleaned = phone.replace(/\D/g, '')
  return cleaned.length === 10 || (cleaned.length === 11 && cleaned.startsWith('1'))
}

/** ZIP code validation (US) */
export function isValidUSZipCode(zip: string): boolean {
  return /^\d{5}(-\d{4})?$/.test(zip)
}

/** Set-aside type validation */
export function isValidSetAsideType(type: string): type is SetAsideType {
  const validTypes: SetAsideType[] = [
    'SB', 'SDB', '8A', 'WOSB', 'EDWOSB', 'VOSB', 'SDVOSB', 'HUBZone', 'ISBEE', 'NONE'
  ]
  return validTypes.includes(type as SetAsideType)
}

/** Validate organization has minimum required fields */
export function validateOrganizationRequired(org: {
  name?: string
  naicsCodes?: NAICSCode[]
}): { valid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!org.name || org.name.trim().length === 0) {
    errors.push('Organization name is required')
  }
  
  if (!org.naicsCodes || org.naicsCodes.length === 0) {
    errors.push('At least one NAICS code is required')
  } else {
    const invalidCodes = org.naicsCodes.filter(c => !isValidNAICSCode(c))
    if (invalidCodes.length > 0) {
      errors.push(`Invalid NAICS codes: ${invalidCodes.join(', ')}`)
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/** Validate opportunity has minimum required fields */
export function validateOpportunityRequired(opp: {
  title?: string
  source?: { system?: string; id?: string }
}): { valid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!opp.title || opp.title.trim().length === 0) {
    errors.push('Opportunity title is required')
  }
  
  if (!opp.source?.system || !opp.source?.id) {
    errors.push('Source system and ID are required')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/** Sanitize string for safe storage/display */
export function sanitizeString(str: string): string {
  return str
    .trim()
    .replace(/[\x00-\x1F\x7F]/g, '') // Remove control characters
    .slice(0, 10000) // Reasonable max length
}

/** Normalize NAICS code (remove dashes, trim) */
export function normalizeNAICSCode(code: string): NAICSCode {
  return code.replace(/\D/g, '').slice(0, 6)
}

