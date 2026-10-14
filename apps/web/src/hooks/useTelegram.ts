import { useEffect } from 'react'

import { tg } from '@/lib/telegram'
import { useAppStore } from '@/store/useAppStore'
import { useUserStore } from '@/store/useUserStore'
import type { Theme } from '@/lib/types'

/** Telegram `themeParams` va `colorScheme`ni CSS o'zgaruvchilarga bog'laydi. */
function applyTelegramTheme() {
  const root = document.documentElement
  const params = tg.themeParams()
  const scheme = tg.colorScheme()

  const fallbacks: Record<string, string> = {
    bg_color: scheme === 'dark' ? '#17212b' : '#ffffff',
    text_color: scheme === 'dark' ? '#f5f5f5' : '#000000',
    hint_color: scheme === 'dark' ? '#7d8b99' : '#999999',
    link_color: '#2ea6ff',
    button_color: '#2ea6ff',
    button_text_color: '#ffffff',
    secondary_bg_color: scheme === 'dark' ? '#232e3c' : '#f1f1f1',
  }

  const map: [string, string][] = [
    ['--tg-bg', params.bg_color || fallbacks.bg_color],
    ['--tg-text', params.text_color || fallbacks.text_color],
    ['--tg-hint', params.hint_color || fallbacks.hint_color],
    ['--tg-link', params.link_color || fallbacks.link_color],
    ['--tg-button', params.button_color || fallbacks.button_color],
    ['--tg-button-text', params.button_text_color || fallbacks.button_text_color],
    ['--tg-secondary-bg', params.secondary_bg_color || fallbacks.secondary_bg_color],
  ]

  map.forEach(([key, value]) => root.style.setProperty(key, value))
}

/**
 * Tema boshqaruvi: foydalanuvchi tanlovi (light/dark/system) yoki Telegram mavzusi.
 * `data-theme` atributi orqali Tailwind darkMode class ishlaydi.
 */
export function useTheme() {
  const theme: Theme = useUserStore((s) => s.user?.theme ?? 'system')
  const setResolvedTheme = useAppStore((s) => s.setResolvedTheme)

  useEffect(() => {
    const root = document.documentElement

    const apply = () => {
      const resolved = theme === 'system' ? tg.colorScheme() : theme
      root.dataset.theme = resolved
      root.classList.toggle('dark', resolved === 'dark')
      setResolvedTheme(resolved)
      if (theme === 'system') applyTelegramTheme()
    }

    apply()

    const unsubscribe = tg.onThemeChanged(apply)
    return unsubscribe
  }, [theme, setResolvedTheme])

  return useAppStore((s) => s.resolvedTheme)
}

/** Telegram WebApp'ni ishga tayyorlaydi (ready + expand). */
export function useTelegramReady() {
  useEffect(() => {
    tg.ready()
  }, [])
}

export type { Theme }
