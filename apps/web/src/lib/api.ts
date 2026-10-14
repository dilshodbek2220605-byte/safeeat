/**
 * Backend bilan ishlash uchun API klient.
 *
 * - `VITE_API_BASE_URL` orqali backend manzili (default: '' → nisbiy /api)
 * - Access token avtomatik `Authorization` sarlavhasiga qo'shiladi
 * - 401 bo'lsa bir marta refresh qilib, so'rovni takrorlaydi
 * - Barcha xatolar `ApiError` ga o'raladi
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || ''

export class ApiError extends Error {
  status: number
  code?: string
  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

// ---- Token saqlash (localStorage) ----
const ACCESS_KEY = 'safeeat.access'
const REFRESH_KEY = 'safeeat.refresh'

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

type Options = RequestInit & { auth?: boolean; isForm?: boolean }

async function rawRequest<T>(path: string, options: Options = {}, retry = true): Promise<T> {
  const { auth = true, isForm = false, headers, ...rest } = options
  const finalHeaders = new Headers(headers)
  if (!isForm && rest.body) finalHeaders.set('Content-Type', 'application/json')
  if (auth && tokenStore.access) finalHeaders.set('Authorization', `Bearer ${tokenStore.access}`)

  const res = await fetch(`${BASE_URL}${path}`, { ...rest, headers: finalHeaders })

  // Token muddati o'tgan — refresh qilib qayta urinamiz
  if (res.status === 401 && auth && retry && tokenStore.refresh) {
    const refreshed = await tryRefresh()
    if (refreshed) return rawRequest<T>(path, options, false)
    tokenStore.clear()
  }

  if (res.status === 204) return undefined as T

  const text = await res.text()
  const data = text ? safeJson(text) : null

  if (!res.ok) {
    const message =
      (data && (data.error?.message || data.detail)) || `So'rov xatosi (${res.status})`
    const code = data?.error?.code
    throw new ApiError(message, res.status, code)
  }
  return data as T
}

function safeJson(text: string): any {
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokenStore.refresh }),
    })
    if (!res.ok) return false
    const data = await res.json()
    tokenStore.set(data.access_token, data.refresh_token)
    return true
  } catch {
    return false
  }
}

export const api = {
  get: <T>(path: string, options?: Options) => rawRequest<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Options) =>
    rawRequest<T>(path, {
      ...options,
      method: 'POST',
      body: body instanceof FormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
      isForm: body instanceof FormData,
    }),
  patch: <T>(path: string, body?: unknown, options?: Options) =>
    rawRequest<T>(path, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  del: <T>(path: string, options?: Options) => rawRequest<T>(path, { ...options, method: 'DELETE' }),
}

/** Absolyut rasm URL'ini yasaydi (backend nisbiy yo'l qaytarsa). */
export function imageUrl(url: string): string {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${BASE_URL}${url}`
}
