import './mobile.css'
import {
  ATTEND_PAGE,
  apiMobileJson,
  clearSession,
  readSession,
  saveSession,
} from './mobile_session'

function mountLoginForm() {
  document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div id="auth-shell" class="auth-shell">
    <div class="auth-brand">근태</div>
    <section class="auth-panel" id="auth-panel-login" aria-label="로그인">
      <h1 class="auth-title">로그인</h1>
      <p class="auth-desc">사원관리에 등록된 사번만 사용합니다. 비밀번호를 처음 쓰는 경우 이름까지 입력하면 DB에 저장된 뒤 로그인됩니다. 다음부터는 사번·비밀번호만 입력하면 됩니다.</p>
      <div class="auth-field">
        <label for="auth-login-no">사번</label>
        <input type="text" id="auth-login-no" autocomplete="username" />
      </div>
      <div class="auth-field">
        <label for="auth-login-name">이름</label>
        <input type="text" id="auth-login-name" autocomplete="name" placeholder="최초 로그인 시에만 (사원관리와 동일)" />
      </div>
      <div class="auth-field">
        <label for="auth-login-pw">비밀번호</label>
        <input type="password" id="auth-login-pw" autocomplete="current-password" />
      </div>
      <div class="auth-field">
        <label for="auth-login-pw2">비밀번호 확인</label>
        <input type="password" id="auth-login-pw2" autocomplete="new-password" />
      </div>
      <p class="auth-error" id="auth-login-err" role="alert" hidden></p>
      <button type="button" class="btn-primary auth-submit" id="auth-login-btn">로그인</button>
    </section>
  </div>
`
  wireLoginForm()
}

function clearAuthFormFields() {
  for (const id of ['auth-login-no', 'auth-login-name', 'auth-login-pw', 'auth-login-pw2']) {
    const el = document.getElementById(id) as HTMLInputElement | null
    if (el) el.value = ''
  }
  const e2 = document.getElementById('auth-login-err')
  if (e2) {
    e2.hidden = true
    e2.textContent = ''
  }
}

function wireLoginForm() {
  document.getElementById('auth-login-btn')?.addEventListener('click', async () => {
    const errEl = document.getElementById('auth-login-err')
    if (errEl) errEl.hidden = true
    const noEl = document.getElementById('auth-login-no') as HTMLInputElement | null
    const nameEl = document.getElementById('auth-login-name') as HTMLInputElement | null
    const pwEl = document.getElementById('auth-login-pw') as HTMLInputElement | null
    const pw2El = document.getElementById('auth-login-pw2') as HTMLInputElement | null
    if (!noEl || !nameEl || !pwEl || !pw2El) return
    const no = noEl.value.trim()
    const nameTrim = nameEl.value.trim()
    const pw = pwEl.value
    const pw2 = pw2El.value
    if (!no || !pw) {
      if (errEl) {
        errEl.textContent = '사번과 비밀번호를 입력하세요.'
        errEl.hidden = false
      }
      return
    }
    if (pw !== pw2) {
      if (errEl) {
        errEl.textContent = '비밀번호와 확인이 일치하지 않습니다.'
        errEl.hidden = false
      }
      return
    }
    try {
      const loginBody: { employee_no: string; password: string; name?: string } = {
        employee_no: no,
        password: pw,
      }
      if (nameTrim) loginBody.name = nameTrim
      const r = await apiMobileJson<{
        access_token: string
        refresh_token: string
        employee_no: string
        name: string
      }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(loginBody),
      })
      saveSession(r.access_token, r.refresh_token, r.employee_no, r.name)
      clearAuthFormFields()
      window.location.replace(ATTEND_PAGE)
    } catch (e) {
      if (errEl) {
        errEl.textContent = String(e)
        errEl.hidden = false
      }
    }
  })
}

async function bootstrapIndex() {
  const s = readSession()
  if (!s?.access_token) {
    mountLoginForm()
    return
  }
  try {
    await apiMobileJson<unknown>('/api/auth/me', { method: 'GET' })
    window.location.replace(ATTEND_PAGE)
  } catch {
    clearSession()
    mountLoginForm()
  }
}

void bootstrapIndex()
