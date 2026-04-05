/**
 * 출근·스캔·기록 UI (attend.html 전용). DOM 주입 후 wireAttendApp 호출.
 */
import { apiMobileJson, clearSession, readSession, INDEX_PAGE } from './mobile_session'

type QrScanModule = typeof import('./mobile_qr_scan')
let qrScanModulePromise: Promise<QrScanModule> | null = null

function getQrScanModule(): Promise<QrScanModule> {
  if (!qrScanModulePromise) {
    qrScanModulePromise = import('./mobile_qr_scan')
  }
  return qrScanModulePromise
}

export function attendAppMarkup(): string {
  return `
  <div id="main-shell" class="main-shell main-shell--full-attend">
  <div class="screens">
    <section class="screen is-active" data-screen="home" aria-label="출근">
      <div class="attend-home-page">
        <header class="screen-header">
          <h1>근태</h1>
        </header>
        <div class="attend-home-main">
          <div class="home-date">
            <div class="home-date-top">
              <div class="home-date-text">
                <div class="date-line" id="home-date-line"></div>
                <div class="date-main">오늘</div>
              </div>
              <div class="home-clock" id="home-clock" aria-live="polite">--:--:--</div>
            </div>
          </div>
          <div class="status-card">
            <div class="label">현재 상태</div>
            <div class="state" id="home-status-state">미출근</div>
            <div class="detail" id="home-status-detail">아직 오늘 출근 기록이 없습니다</div>
          </div>
        </div>
        <div class="attend-home-cta">
          <button type="button" class="btn-primary" id="btn-att-primary">출근하기</button>
        </div>
        <div class="attend-home-spacer" aria-hidden="true"></div>
        <nav class="attend-home-bottom-nav" aria-label="바로가기">
          <button type="button" class="home-bottom-link" data-go-screen="history">기록</button>
          <button type="button" class="home-bottom-link" data-go-screen="more">연차계획</button>
        </nav>
      </div>
    </section>

    <section class="screen" data-screen="scan" aria-label="스캔">
      <div class="attend-scan-page">
        <header class="screen-header">
          <h1 id="scan-title">QR 스캔</h1>
          <p class="sub" id="scan-sub" hidden></p>
        </header>
        <div class="scan-wrap">
          <div id="qr-reader" class="qr-reader-host"></div>
          <div class="scan-overlay scan-overlay--frame" aria-hidden="true">
            <div class="scan-frame"></div>
          </div>
          <p class="scan-hint-in-frame">회사 비치 태블릿의 QR을 프레임 안에 맞춰 주세요.</p>
        </div>
        <p class="scan-digital-clock" id="scan-digital-clock" aria-live="polite">--:--:--</p>
        <p class="scan-err" id="scan-err" role="alert" hidden></p>
        <div class="scan-footer-actions">
          <button type="button" class="scan-mock-success" id="scan-dev-qr" hidden>
            개발: 서버 QR로 처리 (카메라 없음)
          </button>
          <button type="button" class="btn-text" id="scan-cancel">취소</button>
        </div>
      </div>
    </section>

    <section class="screen" data-screen="history" aria-label="기록">
      <header class="screen-header">
        <h1>기록</h1>
        <p class="sub">출퇴근 및 휴가 내역</p>
      </header>
      <div class="leave-summary" id="leave-summary" aria-label="연차·휴가 요약">
        <div class="leave-summary-hd" id="leave-summary-hd">연차·휴가 요약</div>
        <div class="leave-summary-body" id="leave-summary-body">
          <p class="leave-summary-empty">기록 탭을 열면 요약이 표시됩니다.</p>
        </div>
      </div>
      <div class="segment" role="tablist">
        <button type="button" class="is-on" data-seg="att">출퇴근</button>
        <button type="button" data-seg="leave">휴가</button>
      </div>
      <div class="record-list" id="record-att">
        <div class="record-item">
          <div class="left">
            <div class="d">2026.03.28 (금)</div>
            <div class="t">09:01 · 18:05</div>
          </div>
          <span class="badge badge-in">정상</span>
        </div>
        <div class="record-item">
          <div class="left">
            <div class="d">2026.03.27 (목)</div>
            <div class="t">09:15 · 18:02</div>
          </div>
          <span class="badge badge-out">지각</span>
        </div>
        <div class="record-item">
          <div class="left">
            <div class="d">2026.03.26 (수)</div>
            <div class="t">08:58 · 18:00</div>
          </div>
          <span class="badge badge-in">정상</span>
        </div>
      </div>
      <div class="record-list" id="record-leave" hidden>
        <div class="record-item record-item--placeholder">
          <div class="left">
            <div class="d">—</div>
            <div class="t">휴가 기록을 불러오는 중입니다.</div>
          </div>
          <span class="badge badge-muted">—</span>
        </div>
      </div>
    </section>

    <section class="screen" data-screen="more" aria-label="연차계획">
      <header class="screen-header">
        <h1>연차계획</h1>
        <p class="sub">계정 및 설정</p>
      </header>
      <div class="profile-block">
        <div class="avatar" id="profile-avatar" aria-hidden="true">—</div>
        <div>
          <div class="name" id="profile-name">—</div>
          <div class="meta" id="profile-meta">—</div>
        </div>
      </div>
      <nav class="menu-list">
        <button type="button" class="menu-item menu-item--btn" data-go-screen="leave-plan">
          연차사용 계획 <span class="chev">›</span>
        </button>
        <a class="menu-item" href="#">알림 설정 <span class="chev">›</span></a>
        <a class="menu-item" href="#">앱 정보 <span class="chev">›</span></a>
        <a class="menu-item" href="#">문의하기 <span class="chev">›</span></a>
      </nav>
      <button type="button" class="logout">로그아웃</button>
    </section>

    <section class="screen" data-screen="leave-plan" aria-label="연차사용 계획">
      <header class="screen-header screen-header--with-back">
        <button type="button" class="screen-back" data-back-screen="more" aria-label="뒤로">‹</button>
        <div class="screen-header-text">
          <h1>연차사용 계획</h1>
          <p class="sub">사용 예정일을 등록합니다</p>
        </div>
      </header>
      <div class="leave-plan-scroll">
        <p class="leave-plan-msg" id="leave-plan-msg" role="status" hidden></p>
        <div class="leave-plan-card">
          <h2 class="leave-plan-card-title">새 계획</h2>
          <label class="lp-field">
            <span>휴가 종류</span>
            <select id="lp-leave-code"></select>
          </label>
          <label class="lp-field">
            <span>시작일</span>
            <input type="date" id="lp-date-from" />
          </label>
          <label class="lp-field">
            <span>종료일</span>
            <input type="date" id="lp-date-to" />
          </label>
          <label class="lp-field">
            <span>구분</span>
            <select id="lp-unit">
              <option value="FULL">종일</option>
              <option value="AM">오전 반차</option>
              <option value="PM">오후 반차</option>
            </select>
          </label>
          <label class="lp-field">
            <span>사유 (선택)</span>
            <textarea id="lp-reason" rows="3" maxlength="500" placeholder="예: 가족 행사"></textarea>
          </label>
          <button type="button" class="btn-primary lp-submit" id="lp-btn-submit">계획 등록</button>
        </div>
        <h2 class="leave-plan-list-title">내 계획</h2>
        <div class="leave-plan-list" id="leave-plan-list">
          <p class="leave-plan-empty" id="leave-plan-empty">불러오는 중…</p>
        </div>
      </div>
    </section>
  </div>
  </div>

  <nav id="main-tab-bar" class="tab-bar" aria-label="하단 메뉴" hidden>
    <button type="button" class="tab is-active" data-tab="home" aria-current="page">홈</button>
    <button type="button" class="tab" data-tab="history">기록</button>
    <button type="button" class="tab" data-tab="more">연차계획</button>
  </nav>
`
}

type ScanIntent = 'in' | 'out' | null

type TodaySummary = {
  clocked_in: boolean
  last_in_at: string | null
  last_out_at: string | null
}

type MyLeaveSummary = {
  year: number
  items: Array<{
    leave_name: string
    quota_days: number
    used_days: number
    remaining_days: number
  }>
}

type MyLeaveRecord = {
  leave_name: string
  start_date: string
  end_date: string
  work_days: number
  total_days: number
  remaining_days: number | null
}

type LeaveCodeOption = { id: number; code: string; name: string }

type LeavePlanRow = {
  id: number
  leave_name: string
  date_from: string
  date_to: string
  leave_unit: string
  reason: string
  status: string
}

function escHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function fmtYmdDot(iso: string): string {
  const d = iso.length >= 10 ? iso.slice(0, 10) : iso
  const p = d.split('-')
  if (p.length === 3) return `${p[0]}.${p[1]}.${p[2]}`
  return d
}

function leavePlanUnitLabel(u: string): string {
  if (u === 'AM') return '오전 반차'
  if (u === 'PM') return '오후 반차'
  return '종일'
}

function showLeavePlanMsg(text: string, kind: 'ok' | 'err' | '' = ''): void {
  const el = document.getElementById('leave-plan-msg')
  if (!el) return
  el.textContent = text
  el.hidden = !text
  el.classList.remove('leave-plan-msg--ok', 'leave-plan-msg--err')
  if (kind === 'ok') el.classList.add('leave-plan-msg--ok')
  if (kind === 'err') el.classList.add('leave-plan-msg--err')
}

async function refreshLeavePlanScreen(): Promise<void> {
  const sel = document.getElementById('lp-leave-code') as HTMLSelectElement | null
  const listEl = document.getElementById('leave-plan-list')
  if (!sel || !listEl) return
  showLeavePlanMsg('')
  listEl.innerHTML = '<p class="leave-plan-empty" id="leave-plan-empty">불러오는 중…</p>'
  try {
    const codes = await apiMobileJson<LeaveCodeOption[]>('/api/leave-codes', { method: 'GET' })
    const keep = sel.value
    sel.innerHTML = ''
    const opt0 = document.createElement('option')
    opt0.value = ''
    opt0.textContent = codes.length ? '휴가 종류 선택' : '등록된 휴가 코드 없음'
    opt0.disabled = true
    opt0.selected = true
    sel.appendChild(opt0)
    for (const c of codes) {
      const o = document.createElement('option')
      o.value = String(c.id)
      o.textContent = `${c.code} · ${c.name}`
      sel.appendChild(o)
    }
    if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep

    const plans = await apiMobileJson<LeavePlanRow[]>('/api/mobile/leave-plans', { method: 'GET' })
    if (!plans.length) {
      listEl.innerHTML =
        '<p class="leave-plan-empty" id="leave-plan-empty">등록된 사용 계획이 없습니다.</p>'
      return
    }
    listEl.innerHTML = plans
      .map((p) => {
        const range =
          p.date_from.slice(0, 10) === p.date_to.slice(0, 10)
            ? fmtYmdDot(p.date_from)
            : `${fmtYmdDot(p.date_from)} ~ ${fmtYmdDot(p.date_to)}`
        const sub = `${escHtml(p.leave_name)} · ${leavePlanUnitLabel(p.leave_unit)}`
        const reason = p.reason?.trim() ? escHtml(p.reason.trim()) : '—'
        return `<div class="leave-plan-item">
          <div class="leave-plan-item-top">
            <span class="leave-plan-item-date">${range}</span>
            <span class="badge badge-in">${escHtml(p.status === 'PLANNED' ? '계획' : p.status)}</span>
          </div>
          <div class="leave-plan-item-sub">${sub}</div>
          <div class="leave-plan-item-reason">사유: ${reason}</div>
        </div>`
      })
      .join('')
  } catch (e) {
    showLeavePlanMsg(String(e), 'err')
    listEl.innerHTML =
      '<p class="leave-plan-empty" id="leave-plan-empty">목록을 불러오지 못했습니다.</p>'
  }
}

async function refreshLeaveHistory(): Promise<void> {
  const hd = document.getElementById('leave-summary-hd')
  const body = document.getElementById('leave-summary-body')
  const listEl = document.getElementById('record-leave')
  if (!body || !listEl) return
  const y = new Date().getFullYear()
  if (hd) hd.textContent = `${y}년 연차·휴가`
  body.innerHTML = '<p class="leave-summary-empty">불러오는 중…</p>'
  listEl.innerHTML =
    '<div class="record-item record-item--placeholder"><div class="left"><div class="d">—</div><div class="t">불러오는 중…</div></div><span class="badge badge-muted">—</span></div>'
  try {
    const summary = await apiMobileJson<MyLeaveSummary>(`/api/employee-leaves/me/summary?year=${y}`)
    const rows = await apiMobileJson<MyLeaveRecord[]>(`/api/employee-leaves/me?year=${y}`)
    if (!summary.items.length) {
      body.innerHTML =
        '<p class="leave-summary-empty">등록된 휴가 배정이 없습니다. 관리자에서 연도별 배정 후 확인할 수 있습니다.</p>'
    } else {
      body.innerHTML = summary.items
        .map(
          (it) => `
        <div class="leave-summary-row">
          <span class="leave-summary-name">${escHtml(it.leave_name)}</span>
          <span class="leave-summary-nums">배정 ${it.quota_days} · 사용 ${it.used_days} · 잔여 ${it.remaining_days}</span>
        </div>`,
        )
        .join('')
    }
    if (!rows.length) {
      listEl.innerHTML =
        '<div class="record-item record-item--placeholder"><div class="left"><div class="d">—</div><div class="t">해당 연도에 등록된 휴가 사용 기록이 없습니다.</div></div><span class="badge badge-muted">—</span></div>'
    } else {
      listEl.innerHTML = rows
        .map((r) => {
          const range =
            r.start_date.slice(0, 10) === r.end_date.slice(0, 10)
              ? fmtYmdDot(r.start_date)
              : `${fmtYmdDot(r.start_date)} ~ ${fmtYmdDot(r.end_date)}`
          const sub = `${escHtml(r.leave_name)} · 근무일 ${r.work_days}일(주중)`
          const badge =
            r.remaining_days != null ? `잔여 ${r.remaining_days}일` : '—'
          return `<div class="record-item">
          <div class="left">
            <div class="d">${range}</div>
            <div class="t">${sub}</div>
          </div>
          <span class="badge badge-in">${escHtml(badge)}</span>
        </div>`
        })
        .join('')
    }
  } catch {
    body.innerHTML =
      '<p class="leave-summary-empty">연차·휴가 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.</p>'
    listEl.innerHTML =
      '<div class="record-item record-item--placeholder"><div class="left"><div class="d">—</div><div class="t">데이터를 불러오지 못했습니다.</div></div><span class="badge badge-muted">—</span></div>'
  }
}

let pendingIntent: ScanIntent = null
let todaySummary: TodaySummary = {
  clocked_in: false,
  last_in_at: null,
  last_out_at: null,
}

function formatHmFromServer(iso: string | null): string {
  if (!iso) return ''
  const normalized = iso.includes('T') ? iso : iso.replace(' ', 'T')
  const d = new Date(normalized)
  if (Number.isNaN(d.getTime())) return iso.length >= 16 ? iso.slice(11, 16) : iso
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false })
}

async function refreshTodayState(): Promise<void> {
  try {
    todaySummary = await apiMobileJson<TodaySummary>('/api/attendance/today', { method: 'GET' })
  } catch {
    todaySummary = { clocked_in: false, last_in_at: null, last_out_at: null }
  }
}

function syncChromeForScreen(screenName: string) {
  const main = document.getElementById('main-shell')
  const tab = document.getElementById('main-tab-bar')
  const fullAttend = screenName === 'home' || screenName === 'scan'
  if (main) main.classList.toggle('main-shell--full-attend', fullAttend)
  if (tab) tab.hidden = fullAttend
}

function syncProfileFromSession() {
  const s = readSession()
  const nameEl = document.getElementById('profile-name')
  const metaEl = document.getElementById('profile-meta')
  const av = document.getElementById('profile-avatar')
  if (nameEl && s) nameEl.textContent = s.name
  if (metaEl && s) metaEl.textContent = `사번 ${s.employee_no}`
  if (av && s?.name) {
    const ch = s.name.trim().charAt(0)
    av.textContent = ch || '—'
  }
}

function setScreen(name: string) {
  const active = document.querySelector('.screen.is-active')
  const from = active?.getAttribute('data-screen')
  if (from === 'scan' && name !== 'scan') {
    pendingIntent = null
    updateScanCopy()
    void getQrScanModule().then((m) => m.stopAttendQrScanner())
    const errEl = document.getElementById('scan-err')
    if (errEl) {
      errEl.hidden = true
      errEl.textContent = ''
    }
  }

  document.querySelectorAll('.screen').forEach((el) => {
    el.classList.toggle('is-active', el.getAttribute('data-screen') === name)
  })
  document.querySelectorAll('.tab').forEach((el) => {
    const on = el.getAttribute('data-tab') === name
    el.classList.toggle('is-active', on)
    if (el instanceof HTMLButtonElement) {
      el.setAttribute('aria-current', on ? 'page' : 'false')
    }
  })
  syncChromeForScreen(name)

  if (name === 'history') {
    void refreshLeaveHistory()
  }

  if (name === 'leave-plan') {
    void refreshLeavePlanScreen()
  }

  if (name === 'scan') {
    queueMicrotask(() => void beginScanFlow())
  }
}

function updateHomeStatus() {
  const elState = document.getElementById('home-status-state')
  const elDetail = document.getElementById('home-status-detail')
  const btnAtt = document.getElementById('btn-att-primary')
  if (!elState || !elDetail || !btnAtt) return
  const inAt = formatHmFromServer(todaySummary.last_in_at)
  const outAt = formatHmFromServer(todaySummary.last_out_at)
  if (todaySummary.clocked_in) {
    elState.textContent = '출근 완료'
    elDetail.textContent = inAt ? `출근 ${inAt} · 퇴근 전` : '퇴근 전'
    btnAtt.textContent = '퇴근하기'
  } else {
    elState.textContent = '미출근'
    if (todaySummary.last_in_at && todaySummary.last_out_at) {
      elDetail.textContent =
        inAt && outAt ? `오늘 출근 ${inAt} · 퇴근 ${outAt}` : '오늘 기록이 있습니다.'
    } else {
      elDetail.textContent = '아직 오늘 출근 기록이 없습니다'
    }
    btnAtt.textContent = '출근하기'
  }
}

function updateScanCopy() {
  const title = document.getElementById('scan-title')
  const sub = document.getElementById('scan-sub')
  const devBtn = document.getElementById('scan-dev-qr')
  if (!title || !sub) return

  if (pendingIntent === 'in') {
    title.textContent = '출근 · QR 스캔'
  } else if (pendingIntent === 'out') {
    title.textContent = '퇴근 · QR 스캔'
  } else {
    title.textContent = 'QR 스캔'
  }

  sub.hidden = true

  const showDev = import.meta.env.DEV && (pendingIntent === 'in' || pendingIntent === 'out')
  if (devBtn) devBtn.hidden = !showDev
}

async function handleDecodedQr(raw: string) {
  const errEl = document.getElementById('scan-err')
  try {
    const intent = pendingIntent === 'out' ? 'out' : 'in'
    await apiMobileJson<{ ok: boolean }>('/api/attendance/clock-qr', {
      method: 'POST',
      body: JSON.stringify({ qr: raw, intent }),
    })
    pendingIntent = null
    updateScanCopy()
    await refreshTodayState()
    updateHomeStatus()
    setScreen('home')
  } catch (e) {
    if (errEl) {
      errEl.textContent = String(e)
      errEl.hidden = false
    }
    queueMicrotask(() => void beginScanFlow())
  }
}

async function beginScanFlow() {
  const errEl = document.getElementById('scan-err')
  if (errEl && !errEl.textContent) {
    errEl.hidden = true
  }
  const qrScan = await getQrScanModule()
  await qrScan.startAttendQrScanner(
    (text) => void handleDecodedQr(text),
    (msg) => {
      if (errEl) {
        errEl.textContent = msg
        errEl.hidden = false
      }
    },
  )
}

function openScan(intent: ScanIntent) {
  pendingIntent = intent
  updateScanCopy()
  setScreen('scan')
}

function pad2(n: number) {
  return n.toString().padStart(2, '0')
}

export function tickHomeClock() {
  const clockEl = document.getElementById('home-clock')
  const scanClockEl = document.getElementById('scan-digital-clock')
  const dateEl = document.getElementById('home-date-line')
  const now = new Date()
  const hhmmss = `${pad2(now.getHours())}:${pad2(now.getMinutes())}:${pad2(now.getSeconds())}`
  if (clockEl) {
    clockEl.textContent = hhmmss
  }
  if (scanClockEl) {
    scanClockEl.textContent = hhmmss
  }
  if (dateEl) {
    dateEl.textContent = now.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long',
    })
  }
}

export function wireAttendApp() {
  document.querySelectorAll('.tab').forEach((btn) => {
    btn.addEventListener('click', () => {
      const name = btn.getAttribute('data-tab')
      if (!name) return
      setScreen(name)
    })
  })

  document.getElementById('main-shell')?.addEventListener('click', (e) => {
    const back = (e.target as HTMLElement).closest('[data-back-screen]') as HTMLElement | null
    if (back) {
      const to = back.getAttribute('data-back-screen')
      if (to) setScreen(to)
      return
    }
    const el = (e.target as HTMLElement).closest('[data-go-screen]') as HTMLElement | null
    if (!el) return
    const go = el.getAttribute('data-go-screen')
    if (go === 'history' || go === 'more' || go === 'leave-plan') setScreen(go)
  })

  document.querySelectorAll('.segment button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const seg = btn.getAttribute('data-seg')
      document.querySelectorAll('.segment button').forEach((b) => b.classList.toggle('is-on', b === btn))
      const att = document.getElementById('record-att')
      const leave = document.getElementById('record-leave')
      if (att && leave) {
        att.hidden = seg !== 'att'
        leave.hidden = seg !== 'leave'
      }
    })
  })

  document.getElementById('btn-att-primary')?.addEventListener('click', () => {
    openScan(todaySummary.clocked_in ? 'out' : 'in')
  })

  document.getElementById('scan-dev-qr')?.addEventListener('click', () => {
    void (async () => {
      try {
        const r = await fetch('/api/kiosk/attendance-qr')
        if (!r.ok) throw new Error(await r.text())
        const j = (await r.json()) as Record<string, unknown>
        await handleDecodedQr(JSON.stringify(j))
      } catch (e) {
        const errEl = document.getElementById('scan-err')
        if (errEl) {
          errEl.textContent = String(e)
          errEl.hidden = false
        }
      }
    })()
  })

  document.getElementById('scan-cancel')?.addEventListener('click', () => {
    setScreen('home')
  })

  document.getElementById('lp-btn-submit')?.addEventListener('click', () => {
    const sel = document.getElementById('lp-leave-code') as HTMLSelectElement | null
    const fromEl = document.getElementById('lp-date-from') as HTMLInputElement | null
    const toEl = document.getElementById('lp-date-to') as HTMLInputElement | null
    const unitEl = document.getElementById('lp-unit') as HTMLSelectElement | null
    const reasonEl = document.getElementById('lp-reason') as HTMLTextAreaElement | null
    if (!sel || !fromEl || !toEl || !unitEl) return
    const leave_code_id = parseInt(sel.value, 10)
    const date_from = fromEl.value
    const date_to = toEl.value
    const leave_unit = unitEl.value as 'FULL' | 'AM' | 'PM'
    const reason = reasonEl?.value?.trim() ?? ''
    if (!leave_code_id) {
      showLeavePlanMsg('휴가 종류를 선택하세요.', 'err')
      return
    }
    if (!date_from || !date_to) {
      showLeavePlanMsg('시작일과 종료일을 입력하세요.', 'err')
      return
    }
    void (async () => {
      try {
        await apiMobileJson<{ id: number }>('/api/mobile/leave-plans', {
          method: 'POST',
          body: JSON.stringify({
            leave_code_id,
            date_from,
            date_to,
            leave_unit,
            reason,
          }),
        })
        showLeavePlanMsg('계획이 등록되었습니다.', 'ok')
        if (reasonEl) reasonEl.value = ''
        await refreshLeavePlanScreen()
      } catch (err) {
        showLeavePlanMsg(String(err), 'err')
      }
    })()
  })

  document.querySelector('.logout')?.addEventListener('click', () => {
    clearSession()
    window.location.href = INDEX_PAGE
  })

  syncProfileFromSession()
  void refreshTodayState().then(() => {
    updateHomeStatus()
    setScreen('home')
    tickHomeClock()
  })
}

export async function validateAttendSessionOrRedirect(): Promise<boolean> {
  if (!readSession()?.access_token) {
    window.location.replace(INDEX_PAGE)
    return false
  }
  try {
    await apiMobileJson<unknown>('/api/auth/me', { method: 'GET' })
    return true
  } catch {
    clearSession()
    window.location.replace(INDEX_PAGE)
    return false
  }
}
