import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

import { HealthCalendar } from '@/components/dashboard/HealthCalendar'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { useSummary } from '@/hooks/useAnalysis'
import { useUserStore } from '@/store/useUserStore'

/** Bosh sahifa: salomlashish, tahlil tugmasi, statistika va kalendar. */
export function Dashboard() {
  const { t } = useTranslation()
  const user = useUserStore((s) => s.user)
  const { data } = useSummary()

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm text-[var(--tg-hint)]">{t('onboarding.welcome_title')}</p>
          <h1 className="text-2xl font-bold">{user?.first_name ?? t('app.name')}</h1>
        </div>
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--tg-button)]/15 text-lg">
          {user?.photo_url ? (
            <img src={user.photo_url} alt="" className="h-11 w-11 rounded-full object-cover" />
          ) : (
            (user?.first_name?.[0] ?? '🍽️')
          )}
        </span>
      </header>

      <AnalyzeHero />

      {data && data.total_analyses > 0 && (
        <p className="px-1 text-xs text-[var(--tg-hint)]">
          {t('dashboard.total')}: {data.total_analyses} · {t('dashboard.calendar')}
        </p>
      )}

      <StatsCards />
      <HealthCalendar />
    </div>
  )
}

function AnalyzeHero() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  return (
    <button
      type="button"
      onClick={() => navigate('/analyze')}
      className="relative w-full overflow-hidden rounded-3xl bg-gradient-to-br from-sky-500 to-indigo-600 p-5 text-left text-white shadow-lg"
    >
      <div className="relative z-10">
        <div className="mb-2 flex h-11 w-11 items-center justify-center rounded-2xl bg-white/20">
          <span className="text-xl">📷</span>
        </div>
        <p className="text-lg font-bold">{t('dashboard.analyze_now')}</p>
        <p className="mt-0.5 text-sm text-white/80">{t('onboarding.done_subtitle')}</p>
      </div>
      <div className="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-white/10" />
      <div className="absolute -bottom-8 right-10 h-24 w-24 rounded-full bg-white/10" />
    </button>
  )
}
