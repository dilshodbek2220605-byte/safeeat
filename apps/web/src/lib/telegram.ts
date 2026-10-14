/**
 * Telegram WebApp SDK uchun nozik o'ram (wrapper).
 *
 * Brauzerda (Telegram tashqarisida) ham xatosiz ishlashi uchun barcha
 * chaqiruvlar xavfsiz tekshiriladi va "no-op" ga tushadi.
 */
import WebApp from '@twa-dev/sdk'

export type TelegramUser = {
  id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  photo_url?: string
}

export const tg = {
  get raw() {
    return window.Telegram?.WebApp
  },

  /** Ilova Telegram ichida ochilganmi? */
  get isTelegram(): boolean {
    return Boolean(window.Telegram?.WebApp?.initData)
  },

  /** initData satri (backendga yuboriladi) */
  get initData(): string {
    return window.Telegram?.WebApp?.initData ?? ''
  },

  /** Telegram foydalanuvchisi (bo'lmasa null) */
  get user(): TelegramUser | null {
    return (window.Telegram?.WebApp?.initDataUnsafe?.user as TelegramUser) ?? null
  },

  /** @twa-dev/sdk obyekti (qo'shimcha API'lar uchun) */
  get sdk() {
    return WebApp
  },

  ready() {
    try {
      WebApp.ready()
      WebApp.expand()
    } catch {
      /* brauzerda shart emas */
    }
  },

  colorScheme(): 'light' | 'dark' {
    try {
      return (WebApp.colorScheme as 'light' | 'dark') ?? 'light'
    } catch {
      return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
  },

  themeParams(): Record<string, string> {
    try {
      return (WebApp.themeParams as unknown as Record<string, string>) ?? {}
    } catch {
      return {}
    }
  },

  /** Telegram mavzusi o'zgarganda chaqiriladi. */
  onThemeChanged(cb: () => void): () => void {
    try {
      WebApp.onEvent('themeChanged', cb)
      return () => WebApp.offEvent('themeChanged', cb)
    } catch {
      const mq = window.matchMedia?.('(prefers-color-scheme: dark)')
      mq?.addEventListener('change', cb)
      return () => mq?.removeEventListener('change', cb)
    }
  },

  haptic(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'light') {
    try {
      WebApp.HapticFeedback.impactOccurred(style)
    } catch {
      /* noop */
    }
  },

  notify(type: 'error' | 'success' | 'warning') {
    try {
      WebApp.HapticFeedback.notificationOccurred(type)
    } catch {
      /* noop */
    }
  },

  /** Telegram'ning asosiy (MainButton) tugmasini boshqarish. */
  mainButton: {
    show(text: string, onClick: () => void) {
      try {
        WebApp.MainButton.setText(text)
        WebApp.MainButton.onClick(onClick)
        WebApp.MainButton.show()
      } catch {
        /* noop */
      }
    },
    hide() {
      try {
        WebApp.MainButton.hide()
        WebApp.MainButton.offClick(() => {})
      } catch {
        /* noop */
      }
    },
    setLoading(loading: boolean) {
      try {
        if (loading) WebApp.MainButton.showProgress()
        else WebApp.MainButton.hideProgress()
      } catch {
        /* noop */
      }
    },
  },

  /** Telegram BackButton. */
  backButton: {
    show(onClick: () => void) {
      try {
        WebApp.BackButton.onClick(onClick)
        WebApp.BackButton.show()
      } catch {
        /* noop */
      }
    },
    hide() {
      try {
        WebApp.BackButton.hide()
      } catch {
        /* noop */
      }
    },
  },

  isTelegramEnvironment(): boolean {
    try {
      return WebApp.initData.length > 0
    } catch {
      return false
    }
  },
}

/** Foydalanuvchi ismini Telegram'dan oladi (UI uchun). */
export function telegramUser() {
  return tg.sdk?.initDataUnsafe?.user
}
