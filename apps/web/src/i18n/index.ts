import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import en from './en.json'
import ru from './ru.json'
import uz from './uz.json'

export const SUPPORTED_LANGS = ['uz', 'ru', 'en'] as const
export type SupportedLang = (typeof SUPPORTED_LANGS)[number]

/** Telegram `language_code` yoki brauzer tilidan qo'llab-quvvatlanadigan tilni tanlaydi. */
export function detectLanguage(code?: string | null): SupportedLang {
  const value = (code || navigator.language || 'en').toLowerCase()
  if (value.startsWith('uz')) return 'uz'
  if (value.startsWith('ru')) return 'ru'
  return 'en'
}

i18n.use(initReactI18next).init({
  resources: {
    uz: { translation: uz },
    ru: { translation: ru },
    en: { translation: en },
  },
  lng: detectLanguage(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
  returnNull: false,
})

export default i18n
