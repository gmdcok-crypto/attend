import { Html5Qrcode } from 'html5-qrcode'

let current: Html5Qrcode | null = null
let stopChain: Promise<void> = Promise.resolve()

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
  await stopAttendQrScanner()
  if (!document.getElementById('qr-reader')) {
    onFail?.('스캔 영역을 찾을 수 없습니다.')
    return
  }

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
    const cameraId = back?.id ?? cams[0].id

    await html5.start(
      cameraId,
      {
        fps: 10,
        qrbox: (viewW, viewH) => {
          const edge = Math.min(viewW, viewH, 280)
          return { width: edge, height: edge }
        },
      },
      (decoded) => finish(decoded),
      () => {
        /* 매 프레임 — 무시 */
      },
    )
  } catch (e) {
    current = null
    try {
      html5.clear()
    } catch {
      /* */
    }
    onFail?.(e instanceof Error ? e.message : String(e))
  }
}
