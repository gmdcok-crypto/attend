import { Html5Qrcode } from 'html5-qrcode'

let current: Html5Qrcode | null = null
let stopChain: Promise<void> = Promise.resolve()
let startChain: Promise<void> = Promise.resolve()
const SCAN_BOX_EDGE = 300
const START_STABILIZE_MS = 180
const TRANSITION_RETRY_MS = 1000
const MAX_START_ATTEMPTS = 3

export async function stopAttendQrScanner(): Promise<void> {
  stopChain = stopChain.then(async () => {
    if (!current) return
    const h = current
    current = null
    try {
      await h.stop()
    } catch {
      /* 이미 중지됨 */
    }
    try {
      h.clear()
    } catch {
      /* */
    }
  })
  return stopChain
}

/**
 * 후면(또는 첫 번째) 카메라로 QR 스캔. 성공 시 스캔을 멈춘 뒤 onDecoded 호출.
 */
export async function startAttendQrScanner(
  onDecoded: (text: string) => void,
  onFail?: (message: string) => void,
): Promise<void> {
  startChain = startChain.catch(() => {}).then(async () => {
    await stopAttendQrScanner()
    // Some mobile browsers keep camera handle briefly after stop().
    await new Promise((resolve) => setTimeout(resolve, START_STABILIZE_MS))
    if (!document.getElementById('qr-reader')) {
      onFail?.('스캔 영역을 찾을 수 없습니다.')
      return
    }

    for (let attempt = 1; attempt <= MAX_START_ATTEMPTS; attempt += 1) {
      const html5 = new Html5Qrcode('qr-reader', /* verbose */ false)
      current = html5
      let settled = false

      const finish = (text: string) => {
        if (settled) return
        settled = true
        void stopAttendQrScanner().then(() => onDecoded(text))
      }

      try {
        const cams = await Html5Qrcode.getCameras()
        if (!cams.length) {
          current = null
          onFail?.('사용 가능한 카메라가 없습니다.')
          return
        }
        const back = cams.find((c) => /back|rear|environment|후면/i.test(c.label))
        const tried = new Set<string>()
        const candidates: Array<string | MediaTrackConstraints> = [
          { facingMode: { ideal: 'environment' } },
          ...(back ? [back.id] : []),
          ...cams.map((c) => c.id),
        ].filter((c) => {
          if (typeof c !== 'string') return true
          if (tried.has(c)) return false
          tried.add(c)
          return true
        })

        let lastErr: unknown = null
        for (const cam of candidates) {
          try {
            await html5.start(
              cam,
              {
                fps: 10,
                qrbox: (viewW, viewH) => {
                  const edge = Math.min(viewW, viewH, SCAN_BOX_EDGE)
                  return { width: edge, height: edge }
                },
              },
              (decoded) => finish(decoded),
              () => {
                /* 매 프레임 — 무시 */
              },
            )
            return
          } catch (e) {
            lastErr = e
          }
        }
        throw lastErr ?? new Error('could not start video source')
      } catch (e) {
        current = null
        try {
          html5.clear()
        } catch {
          /* */
        }

        const msg = e instanceof Error ? e.message : String(e)
        if (/cannot transition/i.test(msg) && attempt < MAX_START_ATTEMPTS) {
          await new Promise((resolve) => setTimeout(resolve, TRANSITION_RETRY_MS))
          continue
        }
        if (/cannot transition/i.test(msg)) {
          onFail?.('카메라 전환이 반복 실패했습니다. 스캔 화면을 닫았다가 다시 열어주세요.')
          return
        }
        if (/could not start video source/i.test(msg)) {
          onFail?.('카메라를 시작할 수 없습니다. 다른 앱의 카메라 사용을 종료하고 다시 시도해 주세요.')
          return
        }
        onFail?.(msg)
        return
      }
    }
  })
  return startChain
}
