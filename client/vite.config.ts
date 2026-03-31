import { defineConfig } from 'vite'

/** 개발 서버·preview 모두에서 /api → FastAPI 로 넘김 (preview 만 쓸 때 목록이 비는 문제 방지) */
const apiProxy = {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
} as const

export default defineConfig({
  server: {
    /** 같은 Wi‑Fi의 태블릿·폰에서 http://<PC LAN IP>:5173 접속 가능 */
    host: true,
    port: 5173,
    strictPort: true,
    proxy: { ...apiProxy },
  },
  preview: {
    port: 4173,
    proxy: { ...apiProxy },
  },
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        attend: 'attend.html',
        admin: 'admin.html',
        tablet: 'tablet.html',
      },
    },
  },
})
