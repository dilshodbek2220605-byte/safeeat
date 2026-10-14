import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

interface ChipProps {
  active?: boolean
  onClick?: () => void
  children: ReactNode
  className?: string
  disabled?: boolean
}

/** Tanlanadigan "chip" (allergiya/kasallik tugmalari uchun). */
export function Chip({ active, onClick, children, className, disabled }: ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'rounded-full border px-3.5 py-2 text-sm font-medium transition active:scale-95',
        active
          ? 'border-transparent bg-[var(--tg-button)] text-[var(--tg-button-text)] shadow-sm'
          : 'border-black/10 bg-black/[0.03] text-[var(--tg-text)] dark:border-white/15 dark:bg-white/5',
        disabled && 'opacity-50',
        className,
      )}
    >
      {children}
    </button>
  )
}
