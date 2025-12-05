/**
 * NAICS (North American Industry Classification System) types.
 */

/** NAICS code (2-6 digits) */
export type NAICSCode = string

/** NAICS code with description */
export interface NAICSEntry {
  code: NAICSCode
  title: string
  description?: string
}

/** Common IT/Professional Services NAICS codes */
export const COMMON_IT_NAICS: Record<NAICSCode, string> = {
  '541511': 'Custom Computer Programming Services',
  '541512': 'Computer Systems Design Services',
  '541513': 'Computer Facilities Management Services',
  '541519': 'Other Computer Related Services',
  '541611': 'Administrative Management Consulting',
  '541612': 'Human Resources Consulting',
  '541613': 'Marketing Consulting',
  '541614': 'Process, Physical Distribution, and Logistics Consulting',
  '541618': 'Other Management Consulting',
  '541690': 'Other Scientific and Technical Consulting',
  '541715': 'R&D in the Physical, Engineering, and Life Sciences',
  '541720': 'R&D in the Social Sciences and Humanities',
  '541990': 'All Other Professional, Scientific, and Technical Services',
  '518210': 'Data Processing, Hosting, and Related Services',
  '517311': 'Wired Telecommunications Carriers',
  '517312': 'Wireless Telecommunications Carriers',
  '561110': 'Office Administrative Services',
  '561210': 'Facilities Support Services',
  '561320': 'Temporary Help Services',
}

/** PSC (Product Service Code) */
export type PSCCode = string

/** PSC categories */
export interface PSCEntry {
  code: PSCCode
  description: string
  category: string
}

/** Common IT PSC codes */
export const COMMON_IT_PSC: Record<PSCCode, string> = {
  'D302': 'IT and Telecom - Systems Development',
  'D306': 'IT and Telecom - Systems Analysis',
  'D307': 'IT and Telecom - IT Strategy and Architecture',
  'D308': 'IT and Telecom - Programming',
  'D310': 'IT and Telecom - Cyber Security',
  'D311': 'IT and Telecom - Internet Services',
  'D312': 'IT and Telecom - Help Desk',
  'D313': 'IT and Telecom - Computer Aided Design/Manufacturing',
  'D314': 'IT and Telecom - System Acquisition Support',
  'D316': 'IT and Telecom - Telecommunications Network Management',
  'D317': 'IT and Telecom - Automation',
  'D318': 'IT and Telecom - Digitizing',
  'D319': 'IT and Telecom - Other IT and Telecommunications',
  'D399': 'IT and Telecom - Other IT and Telecommunications',
}

/**
 * Get the NAICS sector (2-digit) from a full code.
 */
export function getNAICSSector(code: NAICSCode): NAICSCode {
  return code.substring(0, 2)
}

/**
 * Get the NAICS subsector (3-digit) from a full code.
 */
export function getNAICSSubsector(code: NAICSCode): NAICSCode {
  return code.substring(0, 3)
}

/**
 * Get the NAICS industry group (4-digit) from a full code.
 */
export function getNAICSIndustryGroup(code: NAICSCode): NAICSCode {
  return code.substring(0, 4)
}

/**
 * Check if two NAICS codes are related (share common prefix).
 */
export function areNAICSRelated(code1: NAICSCode, code2: NAICSCode, level: 2 | 3 | 4 = 4): boolean {
  return code1.substring(0, level) === code2.substring(0, level)
}

