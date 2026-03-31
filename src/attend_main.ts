import './mobile.css'
import { attendAppMarkup, tickHomeClock, validateAttendSessionOrRedirect, wireAttendApp } from './mobile_shell'

async function init() {
  const ok = await validateAttendSessionOrRedirect()
  if (!ok) return
  document.querySelector<HTMLDivElement>('#app')!.innerHTML = attendAppMarkup()
  wireAttendApp()
  setInterval(tickHomeClock, 1000)
}

void init()
