/**
 * 모바일 WebView에서 embed/blob PDF 미리보기가 안 될 때용 — PDF.js 캔버스 렌더.
 */
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker

const MAX_PREVIEW_PAGES = 5

export async function renderPdfPreview(host: HTMLElement, data: ArrayBuffer): Promise<void> {
  host.innerHTML = ''
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(data) }).promise
  const pages = Math.min(pdf.numPages, MAX_PREVIEW_PAGES)
  const wrap = host.closest('.lpromo-pdf-wrap') as HTMLElement | null
  const containerWidth = Math.max(
    wrap?.getBoundingClientRect().width ?? 0,
    host.getBoundingClientRect().width ?? 0,
    320,
  )

  for (let i = 1; i <= pages; i++) {
    const page = await pdf.getPage(i)
    const baseViewport = page.getViewport({ scale: 1 })
    const scale = containerWidth / baseViewport.width
    const viewport = page.getViewport({ scale })

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('canvas 2d')
    canvas.width = Math.floor(viewport.width)
    canvas.height = Math.floor(viewport.height)
    canvas.className = 'lpromo-pdf-page-canvas'

    const task = page.render({ canvasContext: ctx, viewport })
    await task.promise

    host.appendChild(canvas)
    if (i < pages) {
      const gap = document.createElement('div')
      gap.className = 'lpromo-pdf-page-gap'
      gap.setAttribute('aria-hidden', 'true')
      host.appendChild(gap)
    }
  }
}
