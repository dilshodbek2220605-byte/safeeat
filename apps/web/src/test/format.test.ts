import { describe, expect, it } from 'vitest'

import { formatCalories, formatNumber, monthName, weekdays } from '@/lib/format'
import { cn } from '@/lib/utils'

describe('format utils', () => {
  it('formats numbers with fallback', () => {
    expect(formatNumber(1234)).toBe('1,234')
    expect(formatNumber(null)).toBe('—')
  })

  it('formats calories', () => {
    expect(formatCalories(450)).toBe('450 kcal')
  })

  it('returns month names per language', () => {
    expect(monthName(1, 'uz')).toBe('Yanvar')
    expect(monthName(1, 'en')).toBe('January')
    expect(monthName(1, 'ru')).toBe('Январь')
  })

  it('returns 7 weekday labels', () => {
    expect(weekdays('en')).toHaveLength(7)
  })
})

describe('cn', () => {
  it('merges conflicting tailwind classes', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4')
    expect(cn('text-sm', false && 'hidden')).toBe('text-sm')
  })
})
