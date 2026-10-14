import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/lib/api'
import type { Analysis, CalendarResponse, Page, RiskLevel, SummaryStats } from '@/lib/types'
import { useUserStore } from '@/store/useUserStore'

// ---- Kalitlar (query keys) ----
export const qk = {
  history: (risk?: RiskLevel | null) => ['analyses', risk ?? 'all'] as const,
  stats: ['stats', 'summary'] as const,
  calendar: (year: number, month: number) => ['stats', 'calendar', year, month] as const,
}

/** Rasm yuklab, AI tahlil qilish. */
export function useAnalyze() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('image', file)
      return api.post<Analysis>('/api/v1/analyses', form)
    },
    onSuccess: () => {
      // Tarix, statistika va kalendarni yangilash
      void qc.invalidateQueries({ queryKey: ['analyses'] })
      void qc.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

/** Tahlillar tarixi. */
export function useHistory(risk?: RiskLevel | null, limit = 30) {
  return useQuery({
    queryKey: qk.history(risk),
    queryFn: () =>
      api.get<Page<Analysis>>(
        `/api/v1/analyses?limit=${limit}${risk ? `&risk=${risk}` : ''}`,
      ),
  })
}

/** Umumiy statistika. */
export function useSummary() {
  return useQuery({
    queryKey: qk.stats,
    queryFn: () => api.get<SummaryStats>('/api/v1/stats/summary'),
  })
}

/** Oylik kalendar. */
export function useCalendar(year: number, month: number) {
  return useQuery({
    queryKey: qk.calendar(year, month),
    queryFn: () => api.get<CalendarResponse>(`/api/v1/stats/calendar?year=${year}&month=${month}`),
  })
}

/** Tahlilni o'chirish. */
export function useDeleteAnalysis() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.del<void>(`/api/v1/analyses/${id}`),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['analyses'] })
      void qc.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

/** Profilni yangilash (server + store). */
export function useUpdateProfile() {
  const setUser = useUserStore((s) => s.setUser)
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      api.patch<import('@/lib/types').User>('/api/v1/users/me', payload),
    onSuccess: (user) => setUser(user),
  })
}
