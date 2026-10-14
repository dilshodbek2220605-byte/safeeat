/** Sonlar va sanalarni formatlash yordamchilari. */

export function formatNumber(n: number | null | undefined, digits = 0): string {
  if (n === null || n === undefined) return '—'
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: digits,
  }).format(n)
}

export function formatCalories(n: number | null | undefined): string {
  return `${formatNumber(n, 0)} kcal`
}

const MONTHS: Record<string, string[]> = {
  uz: ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'],
  ru: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
  en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
}

const WEEKDAYS: Record<string, string[]> = {
  uz: ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'],
  ru: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
  en: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
}

export function monthName(month: number, lang: string): string {
  const list = MONTHS[lang] || MONTHS.en
  return list[month - 1] ?? ''
}

export function weekdays(lang: string): string[] {
  return WEEKDAYS[lang] || WEEKDAYS.en
}

export function formatDate(iso: string | null | undefined, lang = 'uz'): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()} ${monthName(d.getMonth() + 1, lang)}`
}

export function formatDateTime(iso: string | null | undefined, lang = 'uz'): string {
  if (!iso) return ''
  const d = new Date(iso)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${formatDate(iso, lang)} ${hh}:${mm}`
}
