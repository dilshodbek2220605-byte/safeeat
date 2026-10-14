/**
 * Telegram WebApp global obyekti uchun tip e'lonlari.
 *
 * `telegram-web-app.js` skripti `window.Telegram.WebApp`ni yaratadi.
 * @twa-dev/sdk ham shundan foydalanadi — bu yerda minimal tip beramiz.
 */

interface TelegramWebAppUser {
  id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  photo_url?: string
}

interface TelegramHapticFeedback {
  impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void
  notificationOccurred(type: 'error' | 'success' | 'warning'): void
}

interface TelegramButton {
  setText(text: string): void
  onClick(cb: () => void): void
  offClick(cb: () => void): void
  show(): void
  hide(): void
  showProgress(leaveActive?: boolean): void
  hideProgress(): void
}

interface TelegramBackButton {
  onClick(cb: () => void): void
  offClick(cb: () => void): void
  show(): void
  hide(): void
}

interface TelegramWebApp {
  initData: string
  initDataUnsafe: { user?: TelegramWebAppUser }
  colorScheme: 'light' | 'dark'
  themeParams: Record<string, string>
  ready(): void
  expand(): void
  close(): void
  onEvent(event: string, cb: () => void): void
  offEvent(event: string, cb: () => void): void
  HapticFeedback: TelegramHapticFeedback
  MainButton: TelegramButton
  BackButton: TelegramBackButton
}

interface Window {
  Telegram?: { WebApp?: TelegramWebApp }
}
