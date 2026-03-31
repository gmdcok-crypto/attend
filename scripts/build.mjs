/**
 * 로컬: tsc + vite build (cwd: client/)
 * Railway(API 전용): 프론트 빌드 생략 — 백엔드는 requirements.txt + uvicorn 만 사용
 */
import { execSync } from 'node:child_process'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const clientDir = join(scriptDir, '..', 'client')

const onRailway = Boolean(
  process.env.RAILWAY_SERVICE_NAME ||
  process.env.RAILWAY_PROJECT_ID ||
  process.env.RAILWAY_ENVIRONMENT_NAME,
)

if (onRailway) {
  console.log('[build] Railway: API 서비스 — Vite/tsc 생략')
  process.exit(0)
}

execSync('tsc && vite build', { stdio: 'inherit', shell: true, cwd: clientDir })
