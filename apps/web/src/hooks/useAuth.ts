import { useEffect, useState } from 'react'

import { tg } from '@/lib/telegram'
import { useUserStore } from '@/store/useUserStore'

/**
 * Ilova ishga tushganda Telegram `initData` bilan avtomatik autentifikatsiya.
 *
 * - initData mavjud bo'lsa → backendga yuboriladi (HMAC tekshiruvi)
 * - Brauzerda (initData yo'q) → dev uchun xatolik ko'rsatiladi
 */
export function useAuth() {
  const { login, status, user } = useUserStore()
  const [attempted, setAttempted] = useState(false)

  useEffect(() => {
    const initData = tg.isTelegramEnvironment() ? tg.sdk.initData : ''

    // Allaqachon autentifikatsiya qilingan bo'lsa, qayta login qilmaymiz
    if (status === 'authenticated' && user) {
      setAttempted(true)
      return
    }
    if (attempted) return

    if (!initData) {
      setAttempted(true)
      return
    }

    void login(initData).finally(() => setAttempted(true))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return {
    isAuthenticated: status === 'authenticated' && !!user,
    isLoading: !attempted || status === 'loading',
    isError: status === 'error' || (attempted && !tg.isTelegramEnvironment()),
    user,
  }
}
