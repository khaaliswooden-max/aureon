/**
 * Common types used across the Aureon domain.
 */

/** UUID v4 string type */
export type UUID = string

/** ISO 8601 date-time string */
export type ISODateTime = string

/** US State code (2 letters) */
export type StateCode = 
  | 'AL' | 'AK' | 'AZ' | 'AR' | 'CA' | 'CO' | 'CT' | 'DE' | 'FL' | 'GA'
  | 'HI' | 'ID' | 'IL' | 'IN' | 'IA' | 'KS' | 'KY' | 'LA' | 'ME' | 'MD'
  | 'MA' | 'MI' | 'MN' | 'MS' | 'MO' | 'MT' | 'NE' | 'NV' | 'NH' | 'NJ'
  | 'NM' | 'NY' | 'NC' | 'ND' | 'OH' | 'OK' | 'OR' | 'PA' | 'RI' | 'SC'
  | 'SD' | 'TN' | 'TX' | 'UT' | 'VT' | 'VA' | 'WA' | 'WV' | 'WI' | 'WY'
  | 'DC' | 'PR' | 'VI' | 'GU' | 'AS' | 'MP'

/** Country ISO code */
export type CountryCode = string

/** Currency amount in cents/smallest unit */
export type CurrencyAmount = number

/** Percentage as decimal (0.0 to 1.0) */
export type Percentage = number

/** Address structure */
export interface Address {
  line1?: string
  line2?: string
  city?: string
  state?: StateCode
  zipCode?: string
  country?: CountryCode
}

/** Contact information */
export interface Contact {
  name?: string
  email?: string
  phone?: string
  title?: string
}

/** Audit metadata */
export interface AuditMetadata {
  createdAt: ISODateTime
  updatedAt: ISODateTime
  createdBy?: string
  updatedBy?: string
}

/** Source system identifier */
export interface SourceIdentifier {
  system: string
  id: string
  url?: string
}

/** Date range */
export interface DateRange {
  start?: ISODateTime
  end?: ISODateTime
}

/** Monetary range */
export interface MonetaryRange {
  min?: CurrencyAmount
  max?: CurrencyAmount
  currency?: string
}

/** Pagination parameters */
export interface PaginationParams {
  page: number
  pageSize: number
}

/** Paginated response */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

/** Sort order */
export type SortOrder = 'asc' | 'desc'

/** Sort specification */
export interface SortSpec {
  field: string
  order: SortOrder
}

