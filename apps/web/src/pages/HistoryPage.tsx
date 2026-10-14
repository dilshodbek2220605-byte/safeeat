import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Trash2 } from 'lucide-react'

import { ResultSheet } from '@/components/analyze/ResultSheet'
import { PageHeader } from '@/components/layout/AppShell'
import { RiskBadge } from '@/components/ui/RiskBadge'
import { Skeleton } from '@/components/ui/Skeleton'
import { useDeleteAnalysis, useHistory } from '@/hooks/useAnalysis'
import { imageUrl } from '@/lib/api'
import { formatCalories, formatDateTime } from '@/lib/format'
import type { Analysis, RiskLevel } from '@/lib/types'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

const FILTERS: { key: RiskLevel | null; i18n: string }[] = [
  { key: null, i18n: 'history.filter_all' },
  { key: 'safe', i18n: 'history.filter_safe' },
  { key: 'moderate', i18n: 'history.filter_moderate' },
  { key: 'dangerous', i18n: 'history.filter_dangerous' },
]

export function HistoryPage() {
  const { t } = useTranslation()
  const [filter, setFilter] = useState<RiskLevel | null>(null)
  const [selected, setSelected] = useState<Analysis | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)

  const { data, isLoading } = useHistory(filter)
  const del = useDeleteAnalysis()
  const toast = useAppStore((s) => s.toast)

  const open = (a: Analysis) => {
    setSelected(a)
    setSheetOpen(true)
  }

  const remove = async (a: Analysis) => {
    try {
      await del.mutateAsync(a.id)
      toast(t('history.deleted'), 'success')
    } catch {
      toast(t('common.error'), 'error')
    }
  }

  const items = data?.items ?? []

  return (
    <div>
      <PageHeader title={t('history.title')} />

      <div className="no-scrollbar mb-4 flex gap-2 overflow-x-auto">
        {FILTERS.map((f) => (
          <button
            key={f.i18n}
            type="button"
            onClick={() => setFilter(f.key)}
            className={cn(
              'shrink-0 rounded-full px-3.5 py-1.5 text-sm font-medium transition',
              filter === f.key
                ? 'bg-[var(--tg-button)] text-[var(--tg-button-text)]'
                : 'bg-black/5 text-[var(--tg-text)] dark:bg-white/10',
            )}
          >
            {t(f.i18n)}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState title={t('history.empty')} hint={t('history.empty_hint')} />
      ) : (
        <ul className="space-y-2.5">
          {items.map((a) => (
            <li key={a.id}>
              <div className="flex items-center gap-3 rounded-2xl border border-black/5 bg-white/70 p-2.5 dark:border-white/10 dark:bg-white/5">
                <button type="button" onClick={() => open(a)} className="flex min-w-0 flex-1 items-center gap-3 text-left">
                  <img
                    src={imageUrl(a.image_url)}
                    alt=""
                    className="h-14 w-14 shrink-0 rounded-xl object-cover"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-semibold">{a.food_name ?? t('common.loading')}</p>
                    <p className="mt-0.5 truncate text-xs text-[var(--tg-hint)]">
                      {formatDateTime(a.created_at)} · {formatCalories(a.nutrition.calories)}
                    </p>
                    <div className="mt-1.5">
                      <RiskBadge level={a.risk_level} size="sm" />
                    </div>
                  </div>
                </button>
                <button
                  type="button"
                  aria-label="delete"
                  onClick={() => void remove(a)}
                  className="flex h-9 w-9 items-center justify-center rounded-full text-[var(--tg-hint)] hover:bg-rose-500/10 hover:text-rose-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      <ResultSheet analysis={selected} open={sheetOpen} onClose={() => setSheetOpen(false)} />
    </div>
  )
}

function EmptyState({ title, hint }: { title: string; hint: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-20 text-center">
      <span className="text-5xl">🍽️</span>
      <p className="font-semibold">{title}</p>
      <p className="text-sm text-[var(--tg-hint)]">{hint}</p>
    </div>
  )
}
