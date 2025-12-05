/**
 * Set-aside program types for federal procurement.
 */

/** Set-aside type codes */
export type SetAsideType =
  | 'SB'       // Small Business
  | 'SDB'      // Small Disadvantaged Business
  | '8A'       // 8(a) Program
  | 'WOSB'     // Women-Owned Small Business
  | 'EDWOSB'   // Economically Disadvantaged WOSB
  | 'VOSB'     // Veteran-Owned Small Business
  | 'SDVOSB'   // Service-Disabled VOSB
  | 'HUBZone'  // Historically Underutilized Business Zone
  | 'ISBEE'    // Indian Small Business Economic Enterprises
  | 'NONE'     // No set-aside (full & open)

/** Set-aside program details */
export interface SetAsideProgram {
  code: SetAsideType
  name: string
  description: string
  requirements: string[]
  preferenceLevel: number // 1 = highest preference
}

/** Full set-aside program definitions */
export const SET_ASIDE_PROGRAMS: Record<SetAsideType, SetAsideProgram> = {
  'SB': {
    code: 'SB',
    name: 'Small Business Set-Aside',
    description: 'Contracts reserved for small businesses based on size standards',
    requirements: [
      'Meet SBA size standard for relevant NAICS code',
      'Active SAM.gov registration',
      'Small business certification',
    ],
    preferenceLevel: 6,
  },
  'SDB': {
    code: 'SDB',
    name: 'Small Disadvantaged Business',
    description: 'Socially and economically disadvantaged small businesses',
    requirements: [
      'Meet SBA small business size standards',
      'At least 51% owned by disadvantaged individuals',
      'SDB certification or 8(a) participant',
    ],
    preferenceLevel: 5,
  },
  '8A': {
    code: '8A',
    name: '8(a) Business Development Program',
    description: 'SBA program for socially and economically disadvantaged businesses',
    requirements: [
      'Approved 8(a) program participant',
      'Meet 8(a) eligibility requirements',
      'Active participation in business development',
    ],
    preferenceLevel: 1,
  },
  'WOSB': {
    code: 'WOSB',
    name: 'Women-Owned Small Business',
    description: 'Small businesses at least 51% owned and controlled by women',
    requirements: [
      'At least 51% owned by women who are US citizens',
      'Women manage day-to-day operations',
      'Meet SBA size standards',
      'WOSB certification',
    ],
    preferenceLevel: 4,
  },
  'EDWOSB': {
    code: 'EDWOSB',
    name: 'Economically Disadvantaged Women-Owned Small Business',
    description: 'WOSB meeting additional economic disadvantage criteria',
    requirements: [
      'Meet all WOSB requirements',
      'Meet personal net worth requirements',
      'Meet adjusted gross income requirements',
      'EDWOSB certification',
    ],
    preferenceLevel: 3,
  },
  'VOSB': {
    code: 'VOSB',
    name: 'Veteran-Owned Small Business',
    description: 'Small businesses owned and controlled by veterans',
    requirements: [
      'At least 51% owned by veterans',
      'Veterans control management and operations',
      'Meet SBA size standards',
    ],
    preferenceLevel: 5,
  },
  'SDVOSB': {
    code: 'SDVOSB',
    name: 'Service-Disabled Veteran-Owned Small Business',
    description: 'Small businesses owned by service-disabled veterans',
    requirements: [
      'At least 51% owned by service-disabled veteran(s)',
      'Service-disabled veterans control operations',
      'VA or SBA SDVOSB certification',
    ],
    preferenceLevel: 2,
  },
  'HUBZone': {
    code: 'HUBZone',
    name: 'Historically Underutilized Business Zone',
    description: 'Small businesses in designated economically distressed areas',
    requirements: [
      'Principal office in a HUBZone',
      'At least 35% of employees reside in HUBZone',
      'HUBZone certification from SBA',
    ],
    preferenceLevel: 3,
  },
  'ISBEE': {
    code: 'ISBEE',
    name: 'Indian Small Business Economic Enterprises',
    description: 'Small businesses owned by Indian tribes or Alaska Native Corporations',
    requirements: [
      'Owned by federally recognized Indian tribe or ANC',
      'Meet applicable size standards',
      'Appropriate certifications',
    ],
    preferenceLevel: 4,
  },
  'NONE': {
    code: 'NONE',
    name: 'Full and Open Competition',
    description: 'No set-aside restrictions - open to all businesses',
    requirements: [
      'Meet solicitation requirements',
      'Active SAM.gov registration',
    ],
    preferenceLevel: 10,
  },
}

/**
 * Check if an organization's set-aside types qualify for an opportunity's set-aside.
 */
export function isEligibleForSetAside(
  orgSetAsides: SetAsideType[],
  oppSetAside: SetAsideType | null | undefined
): boolean {
  // No set-aside = open to all
  if (!oppSetAside || oppSetAside === 'NONE') {
    return true
  }

  // Direct eligibility
  if (orgSetAsides.includes(oppSetAside)) {
    return true
  }

  // Cross-eligibility rules
  const crossEligibility: Record<SetAsideType, SetAsideType[]> = {
    'SB': ['SB', 'SDB', '8A', 'WOSB', 'EDWOSB', 'VOSB', 'SDVOSB', 'HUBZone'],
    'SDB': ['SDB', '8A'],
    '8A': ['8A'],
    'WOSB': ['WOSB', 'EDWOSB'],
    'EDWOSB': ['EDWOSB'],
    'VOSB': ['VOSB', 'SDVOSB'],
    'SDVOSB': ['SDVOSB'],
    'HUBZone': ['HUBZone'],
    'ISBEE': ['ISBEE'],
    'NONE': [],
  }

  const eligibleTypes = crossEligibility[oppSetAside] || []
  return orgSetAsides.some(type => eligibleTypes.includes(type))
}

