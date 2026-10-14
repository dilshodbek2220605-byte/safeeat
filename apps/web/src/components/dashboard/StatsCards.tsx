import { useTranslation } from 'react-i18next'
import { Activity, Camera, ShieldAlert, ShieldCheck } from 'lucide-react'

import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useSummary } from '@/hooks/useAnalysis'
import { formatNumber } from '@/lib/format'

/** Asosiy statistik kartochkalar to'plami. */
export function StatsCards() {
  const { t } = useTranslation()
  const { data, isLoading } = useSummary()

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20" />
        ))}
      </div>
    )
  }

  const stats = [
    {
      key: 'total',
      label: t('dashboard.total'),
      value: formatNumber(data?.total_analyses),
      icon: Camera,
      color: 'text-sky-500',
    },
    {
      key: 'safe',
      label: t('dashboard.safe'),
      value: formatNumber(data?.safe_count),
      icon: ShieldCheck,
      color: 'text-emerald-500',
    },
    {
      key: 'moderate',
      label: t('dashboard.moderate'),
      value: formatNumber(data?.moderate_count),
      icon: Activity,
      color: 'text-amber-500',
    },
    {
      key: 'dangerous',
      label: t('dashboard.dangerous'),
      value: formatNumber(data?.dangerous_count),
      icon: ShieldAlert,
      color: 'text-rose-500',
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-3">
      {stats.map(({ key, label, value, icon: Icon, color }) => (
        <Card key={key} className="flex items-center gap-3 p-3.5">
          <span className={`rounded-xl bg-black/5 p-2 dark:bg-white/10 ${color}`}>
            <Icon className="h-5 w-5" />
          </span>
          <div className="min-w-0">
            <p className="text-xl font-bold leading-none">{value}</p>
            <p className="mt-1 truncate text-xs text-[var(--tg-hint)]">{label}</p>
          </div>
        </Card>
      ))}
    </div>
  )
}
