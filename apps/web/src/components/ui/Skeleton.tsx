import { cn } from '@/lib/utils'

/** Yuklanish paytida "skeleton" blok. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-lg bg-black/10 dark:bg-white/10', className)} />
}
