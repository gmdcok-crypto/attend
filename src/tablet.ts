import './tablet.css'
import QRCode from 'qrcode'

/** 서버 서명 QR 갱신 주기 (만료 45초와 맞춤) */
const REFRESH_MS = 30_000

/** 첫 줄: 날짜만 (예: 2026년 3월 30일) */
function formatKSTDateLine(d: Date): string {
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(d)
}

/** 둘째 줄: 요일 + 시각 (예: 월요일 14:30:45) */
function formatKSTWeekdayTime(d: Date): string {
  const weekday = new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    weekday: 'long',
  }).format(d)
  const time = new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(d)
  return `${weekday} ${time}`
}

function qrSize(): number {
  const w = Math.min(window.innerWidth - 80, window.innerHeight * 0.45)
  return Math.max(200, Math.min(400, Math.floor(w)))
}

document.querySelector<HTMLDivElement>('#tablet-root')!.innerHTML = `
  <div class="tablet-layout">
    <header class="tablet-header">
      <h1>출근 인증 QR</h1>
    </header>
    <div class="tablet-qr-card">
      <div class="tablet-qr-frame">
        <canvas id="tablet-qr-canvas" aria-label="동적 출근 인증 QR 코드"></canvas>
      </div>
      <dl class="tablet-meta">
        <div>
          <dt>현재 시각</dt>
          <dd class="tablet-clock" id="tablet-clock" aria-live="polite">
            <span class="tablet-clock__date" id="tablet-clock-date">—</span>
            <span class="tablet-clock__line2" id="tablet-clock-line2">—</span>
          </dd>
        </div>
        <div>
          <dt>다음 QR 갱신</dt>
          <dd id="tablet-countdown">—</dd>
        </div>
      </dl>
    </div>
  </div>
`

const canvas = document.getElementById('tablet-qr-canvas') as HTMLCanvasElement
const clockDateEl = document.getElementById('tablet-clock-date')
const clockLine2El = document.getElementById('tablet-clock-line2')
const countdownEl = document.getElementById('tablet-countdown')

let nextRefreshAt = Date.now() + REFRESH_MS

async function drawQr(): Promise<void> {
  try {
    const r = await fetch('/api/kiosk/attendance-qr')
    if (!r.ok) {
      const t = await r.text()
      throw new Error(t || r.statusText)
    }
    const payload = await r.json()
    const text = JSON.stringify(payload)
    const size = qrSize()
    await QRCode.toCanvas(canvas, text, {
      width: size,
      margin: 2,
      color: { dark: '#0b0f17ff', light: '#ffffffff' },
      errorCorrectionLevel: 'M',
    })
    nextRefreshAt = Date.now() + REFRESH_MS
    if (countdownEl) countdownEl.classList.remove('tablet-countdown--error')
  } catch (e) {
    console.error('[tablet] QR API:', e)
    if (countdownEl) {
      countdownEl.textContent = 'API 연결 실패'
      countdownEl.classList.add('tablet-countdown--error')
    }
  }
}

function tick(): void {
  const now = new Date()
  if (clockDateEl) clockDateEl.textContent = formatKSTDateLine(now)
  if (clockLine2El) clockLine2El.textContent = formatKSTWeekdayTime(now)
  if (countdownEl) {
    const sec = Math.max(0, Math.ceil((nextRefreshAt - Date.now()) / 1000))
    countdownEl.textContent = `${sec}초 후`
  }
}

let resizeTimer: ReturnType<typeof setTimeout> | undefined
function scheduleResize(): void {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    drawQr().catch((e) => console.error(e))
  }, 200)
}

drawQr().catch((e) => console.error(e))
setInterval(() => {
  drawQr().catch((e) => console.error(e))
}, REFRESH_MS)

setInterval(tick, 250)
tick()

window.addEventListener('resize', scheduleResize)
