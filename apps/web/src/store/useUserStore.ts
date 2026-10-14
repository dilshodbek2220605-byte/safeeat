import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { Language, Theme, User } from '@/lib/types'
import { api, tokenStore } from '@/lib/api'

type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'error'

interface UserState {
  user: User | null
  status: AuthStatus
  error: string | null

  login: (initData: string) => Promise<void>
  refreshUser: () => Promise<void>
  setUser: (user: User) => void
  logout: () => void
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      status: 'idle',
      error: null,

      async login(initData) {
        set({ status: 'loading', error: null })
        try {
          const res = await api.post<{
            tokens: { access_token: string; refresh_token: string }
            user: User
          }>('/api/v1/auth/telegram', { initData }, { auth: false })

          tokenStore.set(res.tokens.access_token, res.tokens.refresh_token)
          set({ user: res.user, status: 'authenticated', error: null })
        } catch (e) {
          tokenStore.clear()
          set({
            status: 'error',
            error: e instanceof Error ? e.message : 'Auth error',
            user: null,
          })
        }
      },

      async refreshUser() {
        try {
          const user = await api.get<User>('/api/v1/users/me')
          set({ user, status: 'authenticated' })
        } catch {
          // Token yaroqsiz — qayta login kerak
          get().logout()
        }
      },

      setUser(user) {
        set({ user })
      },

      logout() {
        tokenStore.clear()
        set({ user: null, status: 'idle', error: null })
      },
    }),
    {
      name: 'safeeat.user',
      partialize: (s) => ({ user: s.user }),
    },
  ),
)

/** Tildan qulay foydalanish uchun selektor. */
export function currentLanguage(user: User | null): Language {
  return user?.language ?? 'uz'
}

/** Mavzuni qulay olish. */
export function userTheme(user: User | null): Theme {
  return user?.theme ?? 'system'
}
