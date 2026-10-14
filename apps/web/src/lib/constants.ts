import type { Gender, Goal, Language, RiskLevel } from './types'

export const LANGUAGES: { code: Language; label: string; flag: string }[] = [
  { code: 'uz', label: "O'zbekcha", flag: '🇺🇿' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
]

export const GENDERS: { value: Gender; i18n: string }[] = [
  { value: 'male', i18n: 'profile.gender_male' },
  { value: 'female', i18n: 'profile.gender_female' },
  { value: 'other', i18n: 'profile.gender_other' },
]

export const GOALS: { value: Goal; i18n: string; emoji: string }[] = [
  { value: 'lose_weight', i18n: 'profile.goal_lose', emoji: '📉' },
  { value: 'maintain', i18n: 'profile.goal_maintain', emoji: '⚖️' },
  { value: 'gain_weight', i18n: 'profile.goal_gain', emoji: '📈' },
  { value: 'health', i18n: 'profile.goal_health', emoji: '❤️' },
]

/** Surunkali kasalliklar (backend bilan mos kalitlar). */
export const CONDITIONS: { value: string; i18n: string }[] = [
  { value: 'diabetes', i18n: 'conditions.diabetes' },
  { value: 'hypertension', i18n: 'conditions.hypertension' },
  { value: 'celiac', i18n: 'conditions.celiac' },
  { value: 'heart_disease', i18n: 'conditions.heart_disease' },
  { value: 'kidney_disease', i18n: 'conditions.kidney_disease' },
  { value: 'high_cholesterol', i18n: 'conditions.high_cholesterol' },
  { value: 'gout', i18n: 'conditions.gout' },
]

/** Allergiyalar (backend bilan mos kalitlar). */
export const ALLERGIES: { value: string; i18n: string }[] = [
  { value: 'lactose', i18n: 'allergies.lactose' },
  { value: 'nuts', i18n: 'allergies.nuts' },
  { value: 'gluten', i18n: 'allergies.gluten' },
  { value: 'peanut', i18n: 'allergies.peanut' },
  { value: 'egg', i18n: 'allergies.egg' },
  { value: 'soy', i18n: 'allergies.soy' },
  { value: 'fish', i18n: 'allergies.fish' },
  { value: 'shellfish', i18n: 'allergies.shellfish' },
  { value: 'sesame', i18n: 'allergies.sesame' },
]

export const RISK_COLORS: Record<RiskLevel, { bg: string; text: string; ring: string; dot: string }> = {
  safe: { bg: 'bg-emerald-500/15', text: 'text-emerald-600 dark:text-emerald-400', ring: 'ring-emerald-500/30', dot: '#22c55e' },
  moderate: { bg: 'bg-amber-500/15', text: 'text-amber-600 dark:text-amber-400', ring: 'ring-amber-500/30', dot: '#f59e0b' },
  dangerous: { bg: 'bg-red-500/15', text: 'text-rose-600 dark:text-rose-400', ring: 'ring-rose-500/30', dot: '#ef4444' },
}
