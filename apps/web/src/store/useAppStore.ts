import { create } from 'zustand'

type ToastType = 'info' | 'success' | 'error'

interface Toast {
  id: number
  message: string
  type: ToastType
}

interface AppState {
  /** Haqiqiy qo'llanilayotgan tema (themeParams/colorScheme'dan). */
  resolvedTheme: 'light' | 'dark'
  toasts: Toast[]

  setResolvedTheme: (theme: 'light' | 'dark') => void
  toast: (message: string, type?: ToastType) => void
  dismiss: (id: number) => void
}

let toastSeq = 0

export const useAppStore = create<AppState>((set) => ({
  resolvedTheme: 'light',
  toasts: [],

  setResolvedTheme: (resolvedTheme) => set({ resolvedTheme }),

  toast: (message, type = 'info') => {
    const id = ++toastSeq
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 3200)
  },

  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
