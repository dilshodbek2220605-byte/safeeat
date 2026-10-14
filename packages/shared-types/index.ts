/**
 * SafeEat AI — umumiy tiplar (backend Pydantic sxemalarining nusxasi).
 *
 * Bu paket frontend/backend o'rtasidagi AI JSON shartnomasini hujjatlashtiradi.
 * Hozircha faqat tip sifatida ishlatiladi (kod generatsiyasi keyingi qadam).
 */

export type Language = 'uz' | 'ru' | 'en'
export type RiskLevel = 'safe' | 'moderate' | 'dangerous'

/** AI Vision'dan keladigan xom natija (backend `AIResult`). */
export interface AIResult {
  food_name: string
  confidence: number
  portion_estimate_g: number
  nutrition: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
    fiber_g: number
    sugar_g: number
    sodium_mg: number
  }
  ingredients: {
    name: string
    category?: string | null
    is_additive?: boolean
    e_code?: string | null
    risk: RiskLevel
    note?: string | null
  }[]
  additives: { e_code: string | null; name: string; risk: RiskLevel }[]
  allergen_flags: string[]
  base_risk: RiskLevel
  barcode?: { value: string | null; product_name: string | null } | null
}

/** RiskEngine tomonidan qo'shiladigan shaxsiy baho. */
export interface PersonalRisk {
  risk_level: RiskLevel
  risk_score: number
  risk_reasons: { code: string; severity: RiskLevel; message: string; ref: string | null }[]
  personalized_warning: string
}

export const SUPPORTED_LANGUAGES: Language[] = ['uz', 'ru', 'en']

export const ALLERGEN_VOCABULARY = [
  'gluten',
  'lactose',
  'nuts',
  'peanut',
  'egg',
  'soy',
  'fish',
  'shellfish',
  'sesame',
  'honey',
] as const
