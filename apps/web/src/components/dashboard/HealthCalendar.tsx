import { useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { ChevronLeft, ChevronRight } from 'lucide-react'

import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCalendar } from '@/hooks/useAnalysis'
import { RISK_COLORS } from '@/lib/constants'
import { monthName, weekdays } from '@/lib/format'

/** Oylik salomatlik kalendari — kunlik xavf rangini ko'rsatadi. */
export function HealthCalendar() {
  const { t, i18n } = useTranslation()
  const today = new Date()
  const [cursor, setCursor] = useState({ year: today.getFullYear(), month: today.getMonth() + 1 })

  const { data, isLoading } = useCalendar(cursor.year, cursor.month)

  const byDay = new Map<number, { status: keyof typeof RISK_COLORS | null }>()
  data?.days.forEach((d) => {
    byDay.set(new Date(d.day).getDate(), { status: (d.status as keyof typeof RISK_COLORS) ?? null })
  })

  const firstWeekday = (new Date(cursor.year, cursor.month - 1, 1).getDay() + 6) % 7
  const daysInMonth = new Date(cursor.year, cursor.month, 0).getDate()

  const cells: (number | null)[] = [
    ...Array.from({ length: firstWeekday }, () => null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]

  const shift = (delta: number) =>
    setCursor((c) => {
      const d = new Date(c.year, c.month - 1 + delta, 1)
      return { year: d.getFullYear(), month: d.getMonth() + 1 }
    })

  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">{t('dashboard.calendar')}</h3>
        <div className="flex items-center gap-1">
          <IconButton onClick={() => shift(-1)} ariaLabel="prev">
            <ChevronLeft className="h-4 w-4" />
          </IconButton>
          <span className="min-w-[112px] text-center text-sm font-medium">
            {monthName(cursor.month, i18n.language)} {cursor.year}
          </span>
          <IconButton onClick={() => shift(1)} ariaLabel="next">
            <ChevronRight className="h-4 w-4" />
          </IconButton>
        </div>
      </div>

      <div className="mb-1 grid grid-cols-7 gap-1 text-center text-[10px] font-semibold text-[var(--tg-hint)]">
        {weekdays(i18n.language).map((w) => (
          <span key={w}>{w}</span>
        ))}
      </div>

      {isLoading ? (
        <Skeleton className="h-48" />
      ) : (
        <div className="grid grid-cols-7 gap-1">
          {cells.map((dayNum, idx) => {
            if (dayNum === null) return <span key={`empty-${idx}`} />
            const status = byDay.get(dayNum)?.status ?? null
            const isToday =
              today.getFullYear() === cursor.year &&
              today.getMonth() + 1 === cursor.month &&
              today.getDate() === dayNum

            return (
              <div key={dayNum} className="flex aspect-square items-center justify-center">
                <span
                  className={
                    'flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ' +
                    (isToday ? 'ring-1 ring-[var(--tg-button)] ' : '') +
                    (status ? '' : 'text-[var(--tg-hint)]')
                  }
                  style={status ? { backgroundColor: RISK_COLORS[status].dot, color: '#fff' } : undefined}
                  title={status ? t(`result.${status}`, { defaultValue: status }) : undefined}
                >
                  {dayNum}
                </span>
              </div>
            )
          })}
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center justify-center gap-3 text-[11px] text-[var(--tg-hint)]">
        {(['safe', 'moderate', 'dangerous'] as const).map((level) => (
          <span key={level} className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: RISK_COLORS[level].dot }} />
            {t(`result.${level}`, { defaultValue: level })}
          </span>
        ))}
      </div>
    </Card>
  )
}

function IconButton({
  children,
  onClick,
  ariaLabel,
}: {
  children: ReactNode
  onClick: () => void
  ariaLabel: string
}) {
  return (
    <button
      type="button"
      aria-label={ariaLabel}
      onClick={onClick}
      className="flex h-8 w-8 items-center justify-center rounded-full bg-black/5 dark:bg-white/10"
    >
      {children}
    </button>
  )
}
