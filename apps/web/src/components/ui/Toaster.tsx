import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, CheckCircle2, Info } from 'lucide-react'

import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

const ICONS = {
  info: Info,
  success: CheckCircle2,
  error: AlertCircle,
}

const COLORS = {
  info: 'bg-slate-800 text-white',
  success: 'bg-emerald-600 text-white',
  error: 'bg-rose-600 text-white',
}

/** Global bildirishnomalar (toast). */
export function Toaster() {
  const toasts = useAppStore((s) => s.toasts)
  const dismiss = useAppStore((s) => s.dismiss)

  return (
    <div className="pointer-events-none fixed inset-x-0 top-2 z-[100] flex flex-col items-center gap-2 px-4 safe-top">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon = ICONS[toast.type]
          return (
            <motion.button
              key={toast.id}
              onClick={() => dismiss(toast.id)}
              initial={{ opacity: 0, y: -16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              className={cn(
                'pointer-events-auto flex w-full max-w-sm items-center gap-2 rounded-xl px-3.5 py-2.5 text-sm shadow-lg',
                COLORS[toast.type],
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="text-left">{toast.message}</span>
            </motion.button>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
