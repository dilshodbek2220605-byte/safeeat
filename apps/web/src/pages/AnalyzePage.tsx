import { useTranslation } from 'react-i18next'

import { AnalyzePanel } from '@/components/analyze/AnalyzePanel'
import { PageHeader } from '@/components/layout/AppShell'

export function AnalyzePage() {
  const { t } = useTranslation()
  return (
    <div>
      <PageHeader title={t('analyze.title')} subtitle={t('analyze.drop_hint')} />
      <AnalyzePanel />
    </div>
  )
}
