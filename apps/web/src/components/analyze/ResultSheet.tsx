import { useTranslation } from 'react-i18next'
import { AlertTriangle, Info, Leaf } from 'lucide-react'

import { RiskBadge } from '@/components/ui/RiskBadge'
import { Sheet } from '@/components/ui/Sheet'
import { imageUrl } from '@/lib/api'
import { formatCalories, formatNumber } from '@/lib/format'
import type { Analysis } from '@/lib/types'

interface ResultSheetProps {
  analysis: Analysis | null
  open: boolean
  onClose: () => void
}

/** AI tahlil natijasini ko'rsatuvchi pastdan chiqadigan oyna. */
export function ResultSheet({ analysis, open, onClose }: ResultSheetProps) {
  const { t } = useTranslation()
  if (!analysis) return null

  const n = analysis.nutrition

  const nutritionRows = [
    { label: t('analyze.nutrition'), value: formatCalories(n?.calories), primary: true },
    { label: 'Protein', value: `${formatNumber(n?.protein_g, 1)} g` },
    { label: 'Carbs', value: `${formatNumber(n?.carbs_g, 1)} g` },
    { label: 'Fat', value: `${formatNumber(n?.fat_g, 1)} g` },
    { label: 'Sugar', value: `${formatNumber(n?.sugar_g, 1)} g` },
    { label: 'Sodium', value: `${formatNumber(n?.sodium_mg, 0)} mg` },
  ]

  return (
    <Sheet open={open} onClose={onClose} title={t('analyze.result')}>
      <div className="flex gap-3">
        <img
          src={imageUrl(analysis.image_url)}
          alt={analysis.food_name ?? ''}
          className="h-24 w-24 shrink-0 rounded-2xl object-cover"
        />
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-lg font-bold">{analysis.food_name ?? t('analyze.result')}</h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <RiskBadge level={analysis.risk_level} />
            {analysis.portion_estimate_g ? (
              <span className="text-xs text-[var(--tg-hint)]">
                {t('analyze.portion')}: {formatNumber(analysis.portion_estimate_g, 0)} g
              </span>
            ) : null}
          </div>
        </div>
      </div>

      {/* Shaxsiy ogohlantirish */}
      {analysis.personalized_warning && (
        <div className="mt-4 rounded-2xl bg-black/[0.03] p-3.5 dark:bg-white/5">
          <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase text-[var(--tg-hint)]">
            <AlertTriangle className="h-3.5 w-3.5" />
            {t('analyze.warning')}
          </div>
          <p className="text-sm leading-relaxed">{analysis.personalized_warning}</p>
        </div>
      )}

      {/* Ozuqaviy qiymat */}
      <section className="mt-4">
        <h4 className="mb-2 text-sm font-semibold text-[var(--tg-hint)]">{t('analyze.nutrition')}</h4>
        <div className="grid grid-cols-3 gap-2">
          {nutritionRows.map((row) => (
            <div
              key={row.label}
              className="rounded-xl bg-black/[0.03] p-2.5 text-center dark:bg-white/5"
            >
              <div className="text-sm font-bold">{row.value}</div>
              <div className="mt-0.5 truncate text-[10px] text-[var(--tg-hint)]">{row.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* E-qo'shimchalar */}
      <section className="mt-4">
        <h4 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-[var(--tg-hint)]">
          <Leaf className="h-3.5 w-3.5" /> {t('analyze.additives')}
        </h4>
        {analysis.additives.length === 0 ? (
          <p className="text-sm text-[var(--tg-hint)]">{t('analyze.no_additives')}</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {analysis.additives.map((a, i) => (
              <li
                key={`${a.e_code}-${i}`}
                className="rounded-lg border border-black/5 px-2 py-1 text-xs dark:border-white/10"
                title={a.risk}
              >
                {a.e_code ? `${a.e_code} · ` : ''}
                {a.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Tarkib */}
      <section className="mt-4">
        <h4 className="mb-2 text-sm font-semibold text-[var(--tg-hint)]">{t('analyze.ingredients')}</h4>
        {analysis.ingredients.length === 0 ? (
          <p className="text-sm text-[var(--tg-hint)]">{t('analyze.no_ingredients')}</p>
        ) : (
          <ul className="space-y-1.5">
            {analysis.ingredients.map((ing, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--tg-hint)]" />
                <span>
                  {ing.name}
                  {ing.e_code ? ` (${ing.e_code})` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {analysis.confidence != null && (
        <p className="mt-4 flex items-center justify-center gap-1 text-center text-[11px] text-[var(--tg-hint)]">
          <Info className="h-3 w-3" />
          {t('analyze.portion')}: {Math.round((analysis.confidence ?? 0) * 100)}%
        </p>
      )}

      {analysis.personalized_warning && analysis.allergen_matches.length > 0 && (
        <p className="mt-3 flex items-start gap-1.5 text-xs text-rose-500">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          {analysis.allergen_matches.join(', ')}
        </p>
      )}
    </Sheet>
  )
}
