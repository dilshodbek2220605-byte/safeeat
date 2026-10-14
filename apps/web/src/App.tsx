import { useTranslation } from 'react-i18next'
import { Route, Routes } from 'react-router-dom'

import { OnboardingFlow } from '@/components/onboarding/OnboardingFlow'
import { AppShell } from '@/components/layout/AppShell'
import { useAuth } from '@/hooks/useAuth'
import { useTelegramReady, useTheme } from '@/hooks/useTelegram'
import { AnalyzePage } from '@/pages/AnalyzePage'
import { Dashboard } from '@/pages/Dashboard'
import { HistoryPage } from '@/pages/HistoryPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { useUserStore } from '@/store/useUserStore'

export default function App() {
  useTelegramReady()
  useTheme()

  const { isAuthenticated, isLoading, isError } = useAuth()
  const user = useUserStore((s) => s.user)

  if (isLoading) return <Splash />

  if (isError || !isAuthenticated || !user) {
    return <AuthErrorScreen />
  }

  // Onboarding tugallanmagan bo'lsa — birinchi navbatda uni ko'rsatamiz
  if (!user.onboarding_completed) {
    return <OnboardingFlow />
  }

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </AppShell>
  )
}

function Splash() {
  const { t } = useTranslation()
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-4 bg-[var(--tg-bg)]">
      <div className="text-5xl">🥗</div>
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-[var(--tg-button)]/30 border-t-[var(--tg-button)]" />
      <p className="text-sm text-[var(--tg-hint)]">{t('auth.checking')}</p>
    </div>
  )
}

function AuthErrorScreen() {
  const { t } = useTranslation()
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-3 bg-[var(--tg-bg)] px-8 text-center">
      <div className="text-5xl">🔒</div>
      <h1 className="text-lg font-bold">{t('auth.error_title')}</h1>
      <p className="text-sm text-[var(--tg-hint)]">{t('auth.error_hint')}</p>
      <button type="button" onClick={() => location.reload()} className="btn-primary mt-2">
        {t('auth.try_again')}
      </button>
    </div>
  )
}
