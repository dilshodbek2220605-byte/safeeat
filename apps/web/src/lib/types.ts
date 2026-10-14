/** Backend Pydantic sxemalariga mos TypeScript tiplari. */

export type Language = 'uz' | 'ru' | 'en'
export type Theme = 'system' | 'light' | 'dark'
export type Gender = 'male' | 'female' | 'other'
export type Goal = 'lose_weight' | 'maintain' | 'gain_weight' | 'health'
export type RiskLevel = 'safe' | 'moderate' | 'dangerous'
export type AnalysisStatus = 'pending' | 'success' | 'failed'

export interface User {
  id: string
  telegram_id: number
  username: string | null
  first_name: string | null
  last_name: string | null
  photo_url: string | null
  language: Language
  theme: Theme
  age: number | null
  gender: Gender | null
  height_cm: number | null
  weight_kg: number | null
  goal: Goal | null
  chronic_conditions: string[]
  allergies: string[]
  daily_calorie_target: number | null
  onboarding_completed: boolean
  last_seen_at: string | null
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  tokens: TokenPair
  user: User
  is_new_user: boolean
}

export interface Nutrition {
  calories: number | null
  protein_g: number | null
  carbs_g: number | null
  fat_g: number | null
  fiber_g: number | null
  sugar_g: number | null
  sodium_mg: number | null
}

export interface IngredientItem {
  name: string
  category?: string | null
  is_additive?: boolean
  e_code?: string | null
  risk: RiskLevel
  note?: string | null
}

export interface AdditiveItem {
  e_code: string | null
  name: string
  risk: RiskLevel
}

export interface RiskReason {
  code: string
  severity: RiskLevel
  message: string
  ref: string | null
}

export interface Analysis {
  id: string
  image_url: string
  status: AnalysisStatus
  provider: string | null
  food_name: string | null
  confidence: number | null
  portion_estimate_g: number | null
  nutrition: {
    calories: number | null
    protein_g: number | null
    carbs_g: number | null
    fat_g: number | null
    fiber_g: number | null
    sugar_g: number | null
    sodium_mg: number | null
  }
  ingredients: { name: string; category?: string | null; e_code?: string | null; risk: RiskLevel; note?: string | null }[]
  additives: { e_code: string | null; name: string; risk: RiskLevel }[]
  allergen_matches: string[]
  risk_level: RiskLevel | null
  risk_score: number | null
  risk_reasons: RiskReason[]
  personalized_warning: string | null
  created_at: string
}

export interface Page<T> {
  items: T[]
  meta: { total: number; limit: number; offset: number }
}

export interface SummaryStats {
  total_analyses: number
  safe_count: number
  moderate_count: number
  dangerous_count: number
  total_calories: number
  avg_calories: number
  analyses_last_7_days: number
}

export interface CalendarDay {
  day: string
  total: number
  status: RiskLevel | null
  calories: number
}

export interface CalendarResponse {
  year: number
  month: number
  days: CalendarDay[]
}

export interface AuthResponseRaw {
  tokens: { access_token: string; refresh_token: string; token_type: string; expires_in: number }
  user: User
  is_new_user: boolean
}
