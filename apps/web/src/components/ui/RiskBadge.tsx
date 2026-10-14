import { useTranslation } from 'react-i18next'

import { RISK_COLORS } from '@/lib/constants'
import type { RiskLevel } from '@/lib/types'
import { cn } from '@/lib/utils'

interface RiskBadgeProps {
  level: RiskLevel | null | undefined
  size?: 'sm' | 'md'
  className?: string
}

const DOT: Record<RiskLevel, string> = {
  safe: '🟢',
  moderate: '🟡',
  dangerous: '🔴',
}

/** Xavf darajasi belgisi (🟢/🟡/🔴). */
export function RiskBadge({ level, size = 'md', className }: RiskBadgeProps) {
  const { t } = useTranslation()
  const resolved = level ?? 'safe'
  const colors = RISK_COLORS[resolved]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-semibold ring-1',
        size === 'sm' ? 'text-xs' : 'text-sm',
        colors.bg,
        colors.text,
        colors.ring,
        className,
      )}
    >
      <span aria-hidden>{DOT[resolved]}</span>
      {t(`result.${resolved}`, { defaultValue: resolved })}
    </span>
  )
}

export function riskDot(level: RiskLevel | null | undefined): string {
  return DOT[level ?? 'safe']
}
