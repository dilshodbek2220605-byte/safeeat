import type { ReactNode } from 'react'

import { TabBar } from './TabBar'
import { Toaster } from '@/components/ui/Toaster'

/** Asosiy layout: kontent + pastdagi tab paneli. */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-col bg-[var(--tg-bg)]">
      <Toaster />
      <main className="mx-auto w-full max-w-lg flex-1 px-4 pb-32 pt-3 safe-top">{children}</main>
      <TabBar />
    </div>
  )
}

/** Sahifa sarlavhasi (ixtiyoriy tugma bilan). */
export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string
  subtitle?: string
  action?: ReactNode
}) {
  return (
    <header className="mb-4 flex items-start justify-between gap-3">
      <div className="min-w-0">
        <h1 className="truncate text-2xl font-bold leading-tight">{title}</h1>
        {subtitle && <p className="mt-0.5 text-sm text-[var(--tg-hint)]">{subtitle}</p>}
      </div>
      {action}
    </header>
  )
}
