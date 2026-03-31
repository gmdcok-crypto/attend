/** 모바일 로그인 세션 + API (index.html · attend.html 공통) */

export const SESSION_KEY = 'attend_mobile_session_v2'

export type MobileSession = {
  access_token: string
  employee_no: string
  name: string
}

export function authHeaderForFetch(): Record<string, string> {
  const s = readSession()
  if (s?.access_token) return { Authorization: `Bearer ${s.access_token}` }
  return {}
}

export async function apiMobileJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    Accept: 'application/json',
    ...authHeaderForFetch(),
    ...(init?.headers ?? {}),
  }
  if (init?.body != null && !(init.headers && 'Content-Type' in (init.headers as Record<string, string>))) {
    ;(headers as Record<string, string>)['Content-Type'] = 'application/json'
  }
  const r = await fetch(path, { ...init, headers })
  const text = await r.text()
  let data: unknown = null
  if (text) {
    try {
      data = JSON.parse(text) as unknown
    } catch {
      throw new Error(text || r.statusText)
    }
  }
  if (!r.ok) {
    const d = data as { detail?: unknown }
    const msg =
      typeof d?.detail === 'string'
        ? d.detail
        : Array.isArray(d?.detail)
          ? JSON.stringify(d.detail)
          : r.statusText
    throw new Error(msg)
  }
  return data as T
}

export function readSession(): MobileSession | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    const o = JSON.parse(raw) as { access_token?: string; employee_no?: string; name?: string }
    if (o.access_token && o.employee_no && o.name) {
      return { access_token: o.access_token, employee_no: o.employee_no, name: o.name }
    }
  } catch {
    /* ignore */
  }
  return null
}

export function saveSession(access_token: string, employee_no: string, name: string) {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ access_token, employee_no, name }))
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

/** 출근 전용 페이지 (현재 경로 기준 상대) */
export const ATTEND_PAGE = 'attend.html'
export const INDEX_PAGE = 'index.html'
