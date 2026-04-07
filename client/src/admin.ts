import './admin.css'

const titles: Record<string, string> = {
  dashboard: '대시보드',
  dept: '부서코드관리',
  employees: '사원관리',
  leave: '휴가코드설정',
  'leave-emp': '개인별 휴가 관리',
  raw: '원시자료',
  reports: '보고서관리',
  'work-shift': '근무시간 관리',
  'leave-promotion': '연차촉진',
  'admin-settings': '관리자 설정',
}

const ic = {
  home: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V9.5z"/></svg>',
  building:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18M6 12h4M14 12h4M6 16h4M14 16h4M6 8h4M14 8h4"/></svg>',
  users:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  calendar:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
  database:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  file: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>',
  clock:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
  settings:
    '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83l-.12.12a2 2 0 0 1-2.83 0l-.06-.06A1.65 1.65 0 0 0 15 19.4a1.65 1.65 0 0 0-1 .6 1.65 1.65 0 0 0-.33 1v.2a2 2 0 0 1-2 2h-.34a2 2 0 0 1-2-2V21a1.65 1.65 0 0 0-.33-1 1.65 1.65 0 0 0-1-.6 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0l-.12-.12a2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-.6-1 1.65 1.65 0 0 0-1-.33H2.8a2 2 0 0 1-2-2v-.34a2 2 0 0 1 2-2H3a1.65 1.65 0 0 0 1-.33 1.65 1.65 0 0 0 .6-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83l.12-.12a2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-.6 1.65 1.65 0 0 0 .33-1V2.8a2 2 0 0 1 2-2h.34a2 2 0 0 1 2 2V3a1.65 1.65 0 0 0 .33 1 1.65 1.65 0 0 0 1 .6 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0l.12.12a2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9c.08.33.08.67 0 1 .14.38.36.72.66 1 .3.28.66.47 1.05.56.33.08.67.08 1 0"/></svg>',
}

document.querySelector<HTMLDivElement>('#admin-root')!.innerHTML = `
  <div class="admin-layout">
    <aside class="admin-sidebar" aria-label="관리 메뉴">
      <div class="admin-brand">
        <a class="logo" href="/admin.html">
          <span class="mark">근</span>
          <span class="titles">
            <span class="name">근태 관리</span>
            <span class="tag">Admin Console</span>
          </span>
        </a>
      </div>
      <nav class="admin-nav">
        <div class="admin-nav-group">
          <div class="admin-nav-label">메뉴</div>
          <button type="button" class="is-active" data-view="dashboard" data-title="대시보드">
            ${ic.home} 대시보드
          </button>
          <button type="button" data-view="dept" data-title="부서코드관리">
            ${ic.building} 부서코드관리
          </button>
          <button type="button" data-view="employees" data-title="사원관리">
            ${ic.users} 사원관리
          </button>
          <button type="button" data-view="leave" data-title="휴가코드설정">
            ${ic.calendar} 휴가코드설정
          </button>
          <button type="button" data-view="leave-emp" data-title="개인별 휴가 관리">
            ${ic.users} 개인별 휴가 관리
          </button>
          <button type="button" data-view="raw" data-title="원시자료">
            ${ic.database} 원시자료
          </button>
          <button type="button" data-view="reports" data-title="보고서관리">
            ${ic.file} 보고서관리
          </button>
          <button type="button" data-view="work-shift" data-title="근무시간 관리">
            ${ic.clock} 근무시간 관리
          </button>
          <button type="button" data-view="leave-promotion" data-title="연차촉진">
            ${ic.calendar} 연차촉진
          </button>
          <button type="button" data-view="admin-settings" data-title="관리자 설정">
            ${ic.settings} 관리자 설정
          </button>
        </div>
      </nav>
      <div class="admin-sidebar-foot">FastAPI · MariaDB</div>
    </aside>

    <div class="admin-main">
      <header class="admin-topbar" id="admin-topbar">
        <h1 id="admin-page-title">대시보드</h1>
        <div class="admin-topbar-actions">
          <button type="button" class="btn btn-ghost admin-topbar-revoke" id="emp-btn-revoke-auth">
            인증 취소
          </button>
          <div class="admin-user">
            <span class="avatar">관</span>
            <span class="meta">관리자</span>
          </div>
        </div>
      </header>

      <main class="admin-content">
        <section class="admin-view is-active" id="view-dashboard" data-view="dashboard">
          <div class="dashboard-hero">
            <h2>안녕하세요, 관리자님</h2>
            <p>오늘의 근태 현황과 마스터 데이터를 한곳에서 관리하세요.</p>
          </div>
          <div class="stat-grid">
            <div class="stat-card">
              <div class="stat-label">오늘 출근</div>
              <div class="stat-value" id="stat-dash-in">—</div>
              <div class="stat-foot">오늘 IN 기록이 있는 인원</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">미출근</div>
              <div class="stat-value" id="stat-dash-not">—</div>
              <div class="stat-foot">재직 중 · 오늘 아직 출근(IN) 없음</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">지각</div>
              <div class="stat-value" id="stat-dash-late">—</div>
              <div class="stat-foot">첫 출근이 09:00 초과</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">휴가 사용</div>
              <div class="stat-value" id="stat-dash-leave">—</div>
              <div class="stat-foot">오늘 휴가 기간에 해당하는 인원</div>
            </div>
          </div>
          <p class="dashboard-meta" id="stat-dash-date" style="margin: -8px 0 16px; font-size: 0.8125rem; color: var(--a-muted)"></p>
          <div class="panel-grid">
            <div class="panel">
              <div class="panel-hd"><h3>최근 기록</h3></div>
              <div class="panel-bd table-wrap">
                <table class="data-table">
                  <thead>
                    <tr><th>시각</th><th>사원</th><th>유형</th><th>상태</th></tr>
                  </thead>
                  <tbody id="tbody-dashboard-recent">
                    <tr><td colspan="4" class="admin-empty-msg">연결된 기록이 없습니다.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="panel">
              <div class="panel-hd"><h3>바로가기</h3></div>
              <div class="report-list" style="padding-top: 8px">
                <div class="report-item">
                  <div><div class="report-title">원시자료 내보내기</div><div class="report-meta">CSV · 기간 선택</div></div>
                  <button type="button" class="btn btn-ghost">열기</button>
                </div>
                <div class="report-item">
                  <div><div class="report-title">월간 근태 집계</div><div class="report-meta">부서·사원 필터</div></div>
                  <button type="button" class="btn btn-ghost">열기</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-dept" data-view="dept">
          <div class="crud-layout">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-bd table-wrap">
                  <table class="data-table" id="table-dept">
                    <thead>
                      <tr><th>부서코드</th><th>부서명</th></tr>
                    </thead>
                    <tbody id="tbody-dept"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline">
            <div class="form-panel panel form-panel--inline">
              <div class="panel-hd">
                <h3>부서 정보</h3>
                <button type="button" class="btn btn-ghost panel-hd-action">엑셀 업로드</button>
              </div>
              <div class="form-fields form-fields--inline-rows">
                <div class="form-field form-field--row">
                  <label for="dept-code">부서코드</label>
                  <input type="text" id="dept-code" autocomplete="off" placeholder="비우면 D001 형식 자동" readonly aria-readonly="true" />
                </div>
                <div class="form-field form-field--row">
                  <label for="dept-name">부서명</label>
                  <input type="text" id="dept-name" autocomplete="off" placeholder="부서명" />
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-primary" id="dept-btn-add">추가</button>
                <button type="button" class="btn btn-update" id="dept-btn-update">수정</button>
                <button type="button" class="btn btn-danger" id="dept-btn-delete">삭제</button>
              </div>
            </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-employees" data-view="employees">
          <div class="crud-layout crud-layout--emp">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-bd table-wrap">
                  <table class="data-table" id="table-employees">
                    <thead>
                      <tr><th>사번</th><th>이름</th><th>부서</th><th>입사일</th><th>상태</th><th>인증</th></tr>
                    </thead>
                    <tbody id="tbody-employees"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline">
            <div class="form-panel panel form-panel--inline">
              <div class="panel-hd">
                <h3>사원 정보</h3>
                <button type="button" class="btn btn-ghost panel-hd-action">일괄 등록</button>
              </div>
              <div class="form-fields form-fields--inline-rows">
                <div class="form-field form-field--row">
                  <label for="emp-code">사번</label>
                  <input type="text" id="emp-code" autocomplete="off" />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-name">이름</label>
                  <input type="text" id="emp-name" autocomplete="off" />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-dept">부서</label>
                  <select id="emp-dept">
                    <option value="">부서 선택</option>
                  </select>
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-hire">입사일</label>
                  <input type="date" id="emp-hire" />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-base-leave">기준연차</label>
                  <input
                    type="number"
                    id="emp-base-leave"
                    min="0"
                    step="0.5"
                    readonly
                    aria-readonly="true"
                    title="입사일 기준(서버·행 선택 시 갱신). 연차 휴가코드 배정의 기본값으로 쓰입니다."
                  />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-used-leave">사용연차</label>
                  <input
                    type="number"
                    id="emp-used-leave"
                    min="0"
                    step="0.5"
                    value="0"
                    title="연차 휴가코드(기본 V01, 환경변수 ANNUAL_LEAVE_CODE) 기준. 기록(주중 근무일) + 수동 초기분이며, 수정 후 [수정] 저장 시 반영됩니다."
                  />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-remain-leave">잔여연차</label>
                  <input
                    type="number"
                    id="emp-remain-leave"
                    min="0"
                    step="0.5"
                    value="0"
                    readonly
                    aria-readonly="true"
                    title="연도별 배정일 − 사용연차(저장 시 갱신)."
                  />
                </div>
                <div class="form-field form-field--row">
                  <label for="emp-status">상태</label>
                  <select id="emp-status">
                    <option value="재직">재직</option>
                    <option value="휴직">휴직</option>
                    <option value="퇴사">퇴사</option>
                  </select>
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-primary" id="emp-btn-add">추가</button>
                <button type="button" class="btn btn-update" id="emp-btn-update">수정</button>
                <button type="button" class="btn btn-danger" id="emp-btn-delete">삭제</button>
              </div>
            </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-leave" data-view="leave">
          <div class="crud-layout">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-bd table-wrap">
                  <table class="data-table" id="table-leave">
                    <thead>
                      <tr><th>휴가코드</th><th>명칭</th></tr>
                    </thead>
                    <tbody id="tbody-leave"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline">
            <div class="form-panel panel form-panel--inline">
              <div class="panel-hd">
                <h3>휴가 코드</h3>
              </div>
              <div class="form-fields form-fields--inline-rows">
                <div class="form-field form-field--row">
                  <label for="leave-code">휴가코드</label>
                  <input type="text" id="leave-code" autocomplete="off" placeholder="비우면 V01 형식 자동" readonly aria-readonly="true" />
                </div>
                <div class="form-field form-field--row">
                  <label for="leave-name">명칭</label>
                  <input type="text" id="leave-name" autocomplete="off" />
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-primary" id="leave-btn-add">추가</button>
                <button type="button" class="btn btn-update" id="leave-btn-update">수정</button>
                <button type="button" class="btn btn-danger" id="leave-btn-delete">삭제</button>
              </div>
            </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-leave-emp" data-view="leave-emp">
          <div class="page-toolbar page-toolbar--leave-emp">
            <div class="toolbar-row raw-toolbar leave-emp-toolbar">
              <div class="form-field form-field--row">
                <label for="leave-emp-line-q">검색</label>
                <input type="text" id="leave-emp-line-q" autocomplete="off" placeholder="사번·성명" />
              </div>
              <div class="form-field form-field--row">
                <label for="leave-emp-date-from">시작일</label>
                <input type="date" id="leave-emp-date-from" />
              </div>
              <div class="form-field form-field--row">
                <label for="leave-emp-date-to">종료일</label>
                <input type="date" id="leave-emp-date-to" />
              </div>
              <button type="button" class="btn btn-primary" id="leave-emp-btn-search">검색</button>
            </div>
          </div>
          <div class="crud-layout crud-layout--leave-emp">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-bd table-wrap table-wrap--scroll">
                  <table class="data-table data-table--leave-emp" id="table-leave-emp">
                    <thead>
                      <tr>
                        <th>사번</th>
                        <th>성명</th>
                        <th>휴가내용</th>
                        <th>휴가시작</th>
                        <th>휴가종료</th>
                        <th>총일수</th>
                        <th>일수</th>
                        <th>누계</th>
                        <th>남은기간</th>
                      </tr>
                    </thead>
                    <tbody id="tbody-leave-emp"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline">
              <div class="form-panel panel form-panel--inline">
                <div class="panel-hd">
                  <h3>휴가 입력</h3>
                </div>
                <div class="form-fields form-fields--inline-rows">
                  <div class="form-field form-field--row">
                    <label for="leave-emp-no">사번</label>
                    <input type="text" id="leave-emp-no" autocomplete="off" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="leave-emp-name">성명</label>
                    <input type="text" id="leave-emp-name" autocomplete="off" readonly aria-readonly="true" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="leave-emp-code-select">휴가</label>
                    <select id="leave-emp-code-select"></select>
                  </div>
                  <div class="form-field form-field--row">
                    <label for="leave-emp-start">휴가시작일</label>
                    <input type="date" id="leave-emp-start" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="leave-emp-end">휴가종료일</label>
                    <input type="date" id="leave-emp-end" />
                  </div>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn btn-primary" id="leave-emp-btn-save">저장</button>
                  <button type="button" class="btn btn-update" id="leave-emp-btn-update">수정</button>
                  <button type="button" class="btn btn-danger" id="leave-emp-btn-delete">삭제</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-raw" data-view="raw">
          <div class="page-toolbar">
            <div class="toolbar-row raw-toolbar">
              <div class="form-field form-field--row">
                <label for="raw-filter-name">성명</label>
                <input type="text" id="raw-filter-name" autocomplete="name" />
              </div>
              <div class="form-field form-field--row">
                <label for="raw-date-from">시작일</label>
                <input type="date" id="raw-date-from" />
              </div>
              <div class="form-field form-field--row">
                <label for="raw-date-to">종료일</label>
                <input type="date" id="raw-date-to" />
              </div>
            </div>
          </div>
          <div class="crud-layout crud-layout--raw-split">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-hd"><h3>재직 사원</h3></div>
                <div class="panel-bd table-wrap">
                  <table class="data-table" id="table-raw-staff">
                    <thead>
                      <tr><th>사번</th><th>성명</th><th>부서명</th></tr>
                    </thead>
                    <tbody id="tbody-raw-staff"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-hd"><h3>원시자료</h3></div>
                <div class="panel-bd table-wrap table-wrap--raw-log">
                  <table class="data-table" id="table-raw-log">
                    <thead>
                      <tr><th>일자</th><th>구분</th><th>시간</th></tr>
                    </thead>
                    <tbody id="tbody-raw-log"></tbody>
                  </table>
                </div>
              </div>
              <div class="form-panel panel raw-edit-panel">
                <div class="form-fields form-fields--inline-rows raw-edit-fields">
                  <div class="raw-edit-row">
                    <div class="form-field form-field--row">
                      <label for="raw-edit-emp-no">사번</label>
                      <input type="text" id="raw-edit-emp-no" autocomplete="off" />
                    </div>
                    <div class="form-field form-field--row">
                      <label for="raw-edit-emp-name">이름</label>
                      <input type="text" id="raw-edit-emp-name" autocomplete="off" readonly aria-readonly="true" />
                    </div>
                    <div class="form-field form-field--row">
                      <label for="raw-edit-type">구분</label>
                      <select id="raw-edit-type">
                        <option value="IN">출근</option>
                        <option value="OUT">퇴근</option>
                      </select>
                    </div>
                  </div>
                  <div class="raw-edit-row raw-edit-row--compact">
                    <div class="form-field form-field--row">
                      <label for="raw-edit-date">날짜</label>
                      <input type="date" id="raw-edit-date" />
                    </div>
                    <div class="form-field form-field--row">
                      <label for="raw-edit-time">시간</label>
                      <input type="time" id="raw-edit-time" step="1" />
                    </div>
                  </div>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn btn-primary" id="raw-edit-btn-add">추가</button>
                  <button type="button" class="btn btn-update" id="raw-edit-btn-update">수정</button>
                  <button type="button" class="btn btn-danger" id="raw-edit-btn-delete">삭제</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-reports" data-view="reports">
          <div class="page-toolbar">
            <p class="desc">집계·급여·감사용 보고서를 생성·다운로드합니다.</p>
          </div>
          <div class="panel">
            <div class="report-list">
              <div class="report-item">
                <div>
                  <div class="report-title">월별 근태 요약</div>
                  <div class="report-meta">부서별 집계 · PDF / Excel</div>
                </div>
                <button type="button" class="btn btn-primary">생성</button>
              </div>
              <div class="report-item">
                <div>
                  <div class="report-title">지각·조퇴 내역</div>
                  <div class="report-meta">기간·사원 필터</div>
                </div>
                <button type="button" class="btn btn-ghost">생성</button>
              </div>
              <div class="report-item">
                <div>
                  <div class="report-title">휴가 사용 현황</div>
                  <div class="report-meta">코드별 잔여·사용</div>
                </div>
                <button type="button" class="btn btn-ghost">생성</button>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-work-shift" data-view="work-shift">
          <div class="crud-layout">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-bd table-wrap">
                  <table class="data-table" id="table-work-shift">
                    <thead>
                      <tr><th>NO</th><th>근태명</th><th>출근</th><th>퇴근</th></tr>
                    </thead>
                    <tbody id="tbody-work-shift"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline">
              <div class="form-panel panel form-panel--inline">
                <div class="panel-hd">
                  <h3>근무시간</h3>
                </div>
                <div class="form-fields form-fields--inline-rows">
                  <div class="form-field form-field--row">
                    <label for="work-shift-name">근태명</label>
                    <input type="text" id="work-shift-name" autocomplete="off" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="work-shift-in">출근시간</label>
                    <input type="time" id="work-shift-in" step="60" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="work-shift-out">퇴근시간</label>
                    <input type="time" id="work-shift-out" step="60" />
                  </div>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn btn-primary" id="work-shift-btn-add">추가</button>
                  <button type="button" class="btn btn-update" id="work-shift-btn-update">수정</button>
                  <button type="button" class="btn btn-danger" id="work-shift-btn-delete">삭제</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-leave-promotion" data-view="leave-promotion">
          <div class="stat-grid leave-promo-stat-grid">
            <div class="stat-card">
              <div class="stat-label">대상자</div>
              <div class="stat-value" id="lp-stat-target">0</div>
              <div class="stat-foot">검색 조건 기준 촉진 대상 인원</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">미서명</div>
              <div class="stat-value" id="lp-stat-pending">0</div>
              <div class="stat-foot">안내 발송 후 서명 대기 인원</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">1차 발송</div>
              <div class="stat-value" id="lp-stat-first">0</div>
              <div class="stat-foot">1차 안내 발송 완료 인원</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">2차 발송</div>
              <div class="stat-value" id="lp-stat-second">0</div>
              <div class="stat-foot">2차 안내 발송 완료 인원</div>
            </div>
          </div>
          <div class="crud-layout leave-promo-top-layout">
            <div class="crud-table-col">
              <div class="panel">
                <div class="panel-hd"><h3>연차촉진 대상자</h3></div>
                <div class="panel-bd table-wrap table-wrap--leave-promo-targets">
                  <table class="data-table" id="table-leave-promotion-targets">
                    <thead>
                      <tr><th>사번</th><th>성명</th><th>부서</th><th>잔여</th><th>1차</th><th>2차</th><th>서명</th></tr>
                    </thead>
                    <tbody id="tbody-leave-promotion-targets">
                      <tr><td colspan="7" class="admin-empty-msg">조회 버튼을 눌러 대상자를 불러오세요.</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="crud-form-col crud-form-col--inline leave-promo-right-col">
              <div class="form-panel panel form-panel--inline leave-promo-query-form">
                <div class="panel-hd">
                  <h3>조회 조건</h3>
                  <button type="button" class="btn btn-primary leave-promo-hd-search" id="lp-btn-search">
                    조회
                  </button>
                </div>
                <div class="form-fields form-fields--inline-rows">
                  <div class="form-field form-field--row">
                    <label for="lp-campaign-select">캠페인</label>
                    <select id="lp-campaign-select" title="등록된 캠페인 중 조회할 항목을 고릅니다. 새로 등록한 캠페인은 대상이 비어 있을 수 있습니다.">
                      <option value="">—</option>
                    </select>
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-year">기준연도</label>
                    <input type="number" id="lp-year" min="2000" max="2100" placeholder="기준연도" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-dept">부서</label>
                    <select id="lp-dept">
                      <option value="">전체</option>
                    </select>
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-status">서명상태</label>
                    <select id="lp-status">
                      <option value="">전체</option>
                      <option value="pending">미서명</option>
                      <option value="signed">서명완료</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="form-panel panel form-panel--inline leave-promo-config-form">
                <div class="panel-hd"><h3>촉진 안내 설정</h3></div>
                <div class="form-fields form-fields--inline-rows">
                  <div class="form-field form-field--row">
                    <label for="lp-campaign-title">안내 제목</label>
                    <input type="text" id="lp-campaign-title" value="[연차촉진] 연차 사용 촉진 안내" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-doc-version">문서버전</label>
                    <input type="text" id="lp-doc-version" value="v1.0" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-send-date-1">1차 발송일</label>
                    <input type="date" id="lp-send-date-1" />
                  </div>
                  <div class="form-field form-field--row">
                    <label for="lp-send-date-2">2차 발송일</label>
                    <input type="date" id="lp-send-date-2" />
                  </div>
                  <div class="form-field form-field--row leave-promo-config-field--message">
                    <label for="lp-message">안내 문구</label>
                    <textarea id="lp-message" rows="2">연차 사용 촉진 안내문을 확인하시고 서명해 주세요.</textarea>
                  </div>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn btn-primary" id="lp-btn-campaign-save">캠페인 등록</button>
                  <button type="button" class="btn btn-ghost" id="lp-btn-add-all-targets">등록 사원 대상 추가</button>
                  <button type="button" class="btn btn-ghost" id="lp-btn-preview">미리보기</button>
                  <button type="button" class="btn btn-primary" id="lp-btn-send-first">1차 발송</button>
                  <button type="button" class="btn btn-update" id="lp-btn-send-second">2차 발송</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="admin-view" id="view-admin-settings" data-view="admin-settings">
          <div class="crud-layout">
            <div class="crud-form-col" style="max-width: 760px">
              <div class="form-panel panel">
                <div class="panel-hd">
                  <h3>관리자 계정 보안</h3>
                </div>
                <div class="form-fields">
                  <div class="form-field">
                    <label for="admin-login-id">관리자 아이디</label>
                    <input type="text" id="admin-login-id" autocomplete="username" placeholder="admin" />
                  </div>
                  <div class="form-field">
                    <label for="admin-current-pw">현재 비밀번호</label>
                    <input type="password" id="admin-current-pw" autocomplete="current-password" />
                  </div>
                  <div class="form-field">
                    <label for="admin-new-pw">새 비밀번호</label>
                    <input type="password" id="admin-new-pw" autocomplete="new-password" />
                  </div>
                  <div class="form-field">
                    <label for="admin-new-pw2">새 비밀번호 확인</label>
                    <input type="password" id="admin-new-pw2" autocomplete="new-password" />
                  </div>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn btn-primary" id="admin-settings-save">저장</button>
                </div>
                <p class="dashboard-meta" style="margin-top: 10px">
                  관리자 인증(JWT) 연동 전 UI 준비 단계입니다.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
`

function clickTargetElement(e: MouseEvent): Element | null {
  const raw = e.target
  if (raw instanceof Element) return raw
  if (raw instanceof Text && raw.parentElement) return raw.parentElement
  return null
}

/** 다크 테마 알림 (기본 window.alert 대체) */
function adminAlert(message: string): void {
  const overlay = document.createElement('div')
  overlay.className = 'admin-modal-overlay'
  const panel = document.createElement('div')
  panel.className = 'admin-modal'
  panel.setAttribute('role', 'dialog')
  panel.setAttribute('aria-modal', 'true')
  panel.setAttribute('aria-labelledby', 'admin-modal-msg')
  const msg = document.createElement('p')
  msg.id = 'admin-modal-msg'
  msg.className = 'admin-modal__msg'
  msg.textContent = message
  const btn = document.createElement('button')
  btn.type = 'button'
  btn.className = 'btn btn-primary admin-modal__ok'
  btn.textContent = '확인'
  const close = () => {
    overlay.remove()
    document.removeEventListener('keydown', onKey)
  }
  const onKey = (e: KeyboardEvent) => {
    if (e.key === 'Escape') close()
  }
  btn.addEventListener('click', close)
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close()
  })
  document.addEventListener('keydown', onKey)
  panel.appendChild(msg)
  panel.appendChild(btn)
  overlay.appendChild(panel)
  document.body.appendChild(overlay)
  queueMicrotask(() => btn.focus())
}

function bindButtonById(elementId: string, contextLabel: string, handler: () => void): void {
  const btn = document.getElementById(elementId)
  if (!btn) {
    console.error('[admin] 버튼 없음:', elementId)
    return
  }
  btn.addEventListener('click', () => {
    try {
      handler()
    } catch (err) {
      adminAlert(`${contextLabel} 처리 오류: ${String(err)}`)
      console.error(err)
    }
  })
}

type DashboardSummary = {
  date: string
  today_in_count: number
  not_yet_in_count: number
  late_today_count: number
  leave_today_count: number
  recent: Array<{
    occurred_at: string
    event_type: string
    employee_no: string
    employee_name: string
    status_label: string
  }>
}

const DASHBOARD_REFRESH_MS = 5000
let dashboardRefreshTimer: number | null = null
let employeeRealtimeLoad: (() => Promise<void>) | null = null
let employeeEventSource: EventSource | null = null
let employeeRefreshInFlight = false

async function loadDashboard() {
  const s = await apiJson<DashboardSummary>('/api/dashboard/summary')
  const setText = (id: string, v: string) => {
    const el = document.getElementById(id)
    if (el) el.textContent = v
  }
  setText('stat-dash-in', String(s.today_in_count))
  setText('stat-dash-not', String(s.not_yet_in_count))
  setText('stat-dash-late', String(s.late_today_count))
  setText('stat-dash-leave', String(s.leave_today_count))
  const dateEl = document.getElementById('stat-dash-date')
  if (dateEl) dateEl.textContent = `집계 기준일: ${s.date} (KST)`

  const tbody = document.getElementById('tbody-dashboard-recent')
  if (!tbody) return
  tbody.innerHTML = ''
  if (!s.recent.length) {
    const tr = document.createElement('tr')
    tr.innerHTML = '<td colspan="4" class="admin-empty-msg">오늘 기록이 없습니다.</td>'
    tbody.appendChild(tr)
    return
  }
  for (const ev of s.recent) {
    const { day, time } = formatOccurredDisplay(ev.occurred_at)
    const tr = document.createElement('tr')
    const typeLabel = ev.event_type === 'IN' ? '출근' : ev.event_type === 'OUT' ? '퇴근' : ev.event_type
    tr.innerHTML = `<td>${escapeHtml(day)} ${escapeHtml(time)}</td><td>${escapeHtml(ev.employee_name)} (${escapeHtml(
      ev.employee_no,
    )})</td><td>${escapeHtml(typeLabel)}</td><td>${escapeHtml(ev.status_label)}</td>`
    tbody.appendChild(tr)
  }
}

function stopDashboardAutoRefresh() {
  if (dashboardRefreshTimer != null) {
    window.clearInterval(dashboardRefreshTimer)
    dashboardRefreshTimer = null
  }
}

function startDashboardAutoRefresh() {
  stopDashboardAutoRefresh()
  void loadDashboard().catch((e) => console.warn('[admin] dashboard refresh', e))
  dashboardRefreshTimer = window.setInterval(() => {
    void loadDashboard().catch((e) => console.warn('[admin] dashboard refresh', e))
  }, DASHBOARD_REFRESH_MS)
}

function stopEmployeeAutoRefresh() {
  if (employeeEventSource) {
    employeeEventSource.close()
    employeeEventSource = null
  }
}

function startEmployeeAutoRefresh() {
  if (!employeeRealtimeLoad) return
  void employeeRealtimeLoad().catch((e) => console.warn('[admin] employee refresh', e))
  if (employeeEventSource) return

  const es = new EventSource('/api/admin/events')
  employeeEventSource = es
  const triggerLoad = () => {
    if (!employeeRealtimeLoad || employeeRefreshInFlight) return
    employeeRefreshInFlight = true
    void employeeRealtimeLoad()
      .catch((e) => console.warn('[admin] employee refresh', e))
      .finally(() => {
        employeeRefreshInFlight = false
      })
  }
  es.addEventListener('employee_auth', triggerLoad)
  es.onerror = () => {
    // keep the current connection logic simple; browser auto-reconnects EventSource.
  }
}

function showView(id: string) {
  document.querySelectorAll('.admin-view').forEach((el) => {
    el.classList.toggle('is-active', el.getAttribute('data-view') === id)
  })
  document.querySelectorAll('.admin-nav button[data-view]').forEach((btn) => {
    btn.classList.toggle('is-active', btn.getAttribute('data-view') === id)
  })
  const titleEl = document.getElementById('admin-page-title')
  if (titleEl) {
    titleEl.textContent = titles[id] ?? id
  }
  document.getElementById('admin-topbar')?.classList.toggle('admin-topbar--employees', id === 'employees')
  if (id === 'dashboard') startDashboardAutoRefresh()
  else stopDashboardAutoRefresh()
  if (id === 'employees') startEmployeeAutoRefresh()
  else stopEmployeeAutoRefresh()
  if (id === 'raw') loadRawPanel().catch((e) => adminAlert(String(e)))
  if (id === 'leave-emp') refreshLeaveEmpView().catch((e) => adminAlert(String(e)))
  if (id === 'leave-promotion') refreshLeavePromotionView().catch((e) => adminAlert(String(e)))
}

document.querySelector('.admin-nav')?.addEventListener('click', (e) => {
  const el = clickTargetElement(e as MouseEvent)
  const navBtn = el?.closest('button[data-view]')
  if (!navBtn) return
  const id = navBtn.getAttribute('data-view')
  if (id) showView(id)
})

function escapeHtml(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

type DeptRow = { id: number; code: string; name: string }
type LeaveRow = { id: number; code: string; name: string }
type WorkShiftRow = {
  id: number
  name: string
  clock_in: string
  clock_out: string
  sort_order: number
}
type EmpLeaveListRow = {
  id: number
  employee_id: number
  employee_no: string
  name: string
  leave_code_id: number
  leave_code: string
  leave_name: string
  start_date: string
  end_date: string
  total_days: number
  work_days: number
  cumulative_work_days: number
  initial_used_days?: number
  remaining_days: number | null
}
type EmpRow = {
  id: number
  employee_no: string
  name: string
  department_name: string | null
  hire_date: string
  status: string
  auth_status: string
}

type LpCampaignRow = {
  id: number
  title: string
  doc_version: string
  doc_hash: string
  created_at: string | null
  target_count: number
  signed_count: number
  first_sent_count: number
  second_sent_count: number
}

type LpTargetRow = {
  employee_id: number
  employee_no: string
  name: string
  department_name: string | null
  remaining_days: number | null
  read_at: string | null
  signed_at: string | null
  first_sent_at: string | null
  second_sent_at: string | null
}

type AttEvent = {
  id: number
  event_type: string
  occurred_at: string
  employee_no: string
  employee_name: string
}

function formatLocalDateYMD(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function hireInputValue(iso: string): string {
  return iso.length >= 10 ? iso.slice(0, 10) : iso
}

function calcBaseAnnualLeaveByHireDate(hireDateIso: string): string {
  if (!hireDateIso) return ''
  const hire = new Date(hireDateIso)
  if (Number.isNaN(hire.getTime())) return ''
  const now = new Date()
  const years = now.getFullYear() - hire.getFullYear() - (now < new Date(now.getFullYear(), hire.getMonth(), hire.getDate()) ? 1 : 0)
  if (years < 1) {
    const months =
      (now.getFullYear() - hire.getFullYear()) * 12 +
      (now.getMonth() - hire.getMonth()) -
      (now.getDate() < hire.getDate() ? 1 : 0)
    return String(Math.max(0, Math.min(11, months)))
  }
  const extra = Math.floor((years - 1) / 2)
  return String(Math.min(25, 15 + Math.max(0, extra)))
}

function httpDetail(data: unknown): string {
  if (data == null) return '요청 실패'
  if (typeof data === 'string') return data
  if (typeof data === 'object' && 'detail' in data) {
    const d = (data as { detail: unknown }).detail
    if (typeof d === 'string') return d
    if (Array.isArray(d)) return JSON.stringify(d)
    return JSON.stringify(d)
  }
  return JSON.stringify(data)
}

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: HeadersInit = { Accept: 'application/json', ...(init?.headers ?? {}) }
  if (init?.body != null && !(init.headers && 'Content-Type' in (init.headers as Record<string, string>))) {
    ;(headers as Record<string, string>)['Content-Type'] = 'application/json'
  }
  const r = await fetch(path, { ...init, headers })
  if (r.status === 204) {
    return undefined as T
  }
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
    throw new Error(httpDetail(data))
  }
  return data as T
}

function initRawToolbarDates() {
  const today = formatLocalDateYMD(new Date())
  const fromEl = document.getElementById('raw-date-from') as HTMLInputElement | null
  const toEl = document.getElementById('raw-date-to') as HTMLInputElement | null
  if (fromEl) fromEl.value = today
  if (toEl) toEl.value = today
}

let rawPanelWired = false
let rawStaffCache: EmpRow[] = []
let selectedRawEmpId: number | null = null
let selectedRawEventId: number | null = null

function formatOccurredDisplay(iso: string): { day: string; time: string } {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) {
    return { day: iso.slice(0, 10), time: iso.slice(11) || '—' }
  }
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return { day: `${y}-${m}-${day}`, time: `${hh}:${mm}:${ss}` }
}

function renderRawStaffTable() {
  const tbody = document.getElementById('tbody-raw-staff')
  if (!tbody) return
  const nameFilter =
    (document.getElementById('raw-filter-name') as HTMLInputElement | null)?.value?.trim().toLowerCase() ?? ''
  let rows = rawStaffCache.filter((e) => e.status === '재직')
  if (nameFilter) {
    rows = rows.filter((e) => e.name.toLowerCase().includes(nameFilter))
  }
  tbody.innerHTML = ''
  for (const e of rows) {
    const tr = document.createElement('tr')
    tr.tabIndex = 0
    tr.dataset.id = String(e.id)
    if (selectedRawEmpId === e.id) tr.classList.add('is-selected')
    tr.innerHTML = `<td>${escapeHtml(e.employee_no)}</td><td>${escapeHtml(e.name)}</td><td>${escapeHtml(
      e.department_name ?? '',
    )}</td>`
    tbody.appendChild(tr)
  }
  if (!rows.length) {
    const tr = document.createElement('tr')
    tr.innerHTML = '<td colspan="3" class="admin-empty-msg">데이터가 없습니다</td>'
    tbody.appendChild(tr)
  }
}

async function loadRawStaff() {
  const rows = await apiJson<EmpRow[]>('/api/employees')
  rawStaffCache = rows
  renderRawStaffTable()
}

async function loadRawEvents() {
  const tbody = document.getElementById('tbody-raw-log')
  const fromEl = document.getElementById('raw-date-from') as HTMLInputElement | null
  const toEl = document.getElementById('raw-date-to') as HTMLInputElement | null
  if (!tbody || !fromEl || !toEl) return
  const dateFrom = fromEl.value
  const dateTo = toEl.value
  if (!dateFrom || !dateTo) return
  const params = new URLSearchParams({ date_from: dateFrom, date_to: dateTo })
  if (selectedRawEmpId != null) {
    params.set('employee_id', String(selectedRawEmpId))
  } else {
    const nm = (document.getElementById('raw-filter-name') as HTMLInputElement | null)?.value?.trim()
    if (nm) params.set('employee_name', nm)
  }
  const events = await apiJson<AttEvent[]>(`/api/attendance-events?${params.toString()}`)
  tbody.innerHTML = ''
  const selectedBefore = selectedRawEventId
  selectedRawEventId = null
  for (const ev of events) {
    const { day, time } = formatOccurredDisplay(ev.occurred_at)
    const tr = document.createElement('tr')
    tr.dataset.id = String(ev.id)
    tr.dataset.employeeNo = ev.employee_no
    tr.dataset.employeeName = ev.employee_name
    tr.dataset.eventType = ev.event_type
    tr.dataset.eventDate = day
    tr.dataset.eventTime = time
    if (selectedBefore === ev.id) {
      tr.classList.add('is-selected')
      selectedRawEventId = ev.id
    }
    const typeLabel = ev.event_type === 'IN' ? '출근' : ev.event_type === 'OUT' ? '퇴근' : ev.event_type
    tr.innerHTML = `<td>${escapeHtml(day)}</td><td>${escapeHtml(typeLabel)}</td><td>${escapeHtml(time)}</td>`
    tbody.appendChild(tr)
  }
  if (!events.length) {
    const tr = document.createElement('tr')
    tr.innerHTML = '<td colspan="3" class="admin-empty-msg">데이터가 없습니다</td>'
    tbody.appendChild(tr)
  }
}

function fillRawEditFormFromRow(tr: HTMLTableRowElement) {
  const noEl = document.getElementById('raw-edit-emp-no') as HTMLInputElement | null
  const nameEl = document.getElementById('raw-edit-emp-name') as HTMLInputElement | null
  const typeEl = document.getElementById('raw-edit-type') as HTMLSelectElement | null
  const dateEl = document.getElementById('raw-edit-date') as HTMLInputElement | null
  const timeEl = document.getElementById('raw-edit-time') as HTMLInputElement | null
  if (!noEl || !nameEl || !typeEl || !dateEl || !timeEl) return
  noEl.value = tr.dataset.employeeNo ?? ''
  nameEl.value = tr.dataset.employeeName ?? ''
  typeEl.value = tr.dataset.eventType === 'OUT' ? 'OUT' : 'IN'
  dateEl.value = tr.dataset.eventDate ?? ''
  const rawTime = tr.dataset.eventTime ?? ''
  timeEl.value = rawTime.length >= 8 ? rawTime.slice(0, 8) : rawTime
}

function clearRawEditSelection() {
  selectedRawEventId = null
  document.querySelectorAll('#tbody-raw-log tr').forEach((r) => r.classList.remove('is-selected'))
}

function wireRawPanelOnce() {
  const debounce = (fn: () => void, ms: number) => {
    let t: number | undefined
    return () => {
      window.clearTimeout(t)
      t = window.setTimeout(fn, ms)
    }
  }
  const reloadDebounced = debounce(() => {
    loadRawEvents().catch((e) => adminAlert(String(e)))
  }, 350)

  document.getElementById('raw-date-from')?.addEventListener('change', () => {
    loadRawEvents().catch((e) => adminAlert(String(e)))
  })
  document.getElementById('raw-date-to')?.addEventListener('change', () => {
    loadRawEvents().catch((e) => adminAlert(String(e)))
  })
  document.getElementById('raw-filter-name')?.addEventListener('input', () => {
    selectedRawEmpId = null
    renderRawStaffTable()
    reloadDebounced()
  })

  document.getElementById('tbody-raw-staff')?.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    const tbody = document.getElementById('tbody-raw-staff')
    if (!tr || !tbody || tr.parentElement !== tbody || !tr.dataset.id) return
    const id = parseInt(tr.dataset.id, 10)
    if (Number.isNaN(id)) return
    if (selectedRawEmpId === id) {
      selectedRawEmpId = null
    } else {
      selectedRawEmpId = id
    }
    renderRawStaffTable()
    loadRawEvents().catch((err) => adminAlert(String(err)))
  })

  document.getElementById('tbody-raw-log')?.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    const tbody = document.getElementById('tbody-raw-log')
    if (!tr || !tbody || tr.parentElement !== tbody || !tr.dataset.id) return
    clearRawEditSelection()
    tr.classList.add('is-selected')
    selectedRawEventId = parseInt(tr.dataset.id, 10)
    fillRawEditFormFromRow(tr as HTMLTableRowElement)
  })

  const resolveNameByNo = () => {
    const noEl = document.getElementById('raw-edit-emp-no') as HTMLInputElement | null
    const nameEl = document.getElementById('raw-edit-emp-name') as HTMLInputElement | null
    if (!noEl || !nameEl) return
    const no = noEl.value.trim()
    if (!no) {
      nameEl.value = ''
      return
    }
    apiJson<{ name: string }>(`/api/employees/by-number/${encodeURIComponent(no)}`)
      .then((r) => {
        nameEl.value = r.name
      })
      .catch(() => {
        nameEl.value = ''
      })
  }
  document.getElementById('raw-edit-emp-no')?.addEventListener('blur', resolveNameByNo)

  bindButtonById('raw-edit-btn-add', '원시자료', () => {
    const no = (document.getElementById('raw-edit-emp-no') as HTMLInputElement | null)?.value?.trim() ?? ''
    const typ = (document.getElementById('raw-edit-type') as HTMLSelectElement | null)?.value ?? 'IN'
    const dt = (document.getElementById('raw-edit-date') as HTMLInputElement | null)?.value ?? ''
    const tm = (document.getElementById('raw-edit-time') as HTMLInputElement | null)?.value ?? ''
    if (!no || !dt || !tm) {
      adminAlert('사번·날짜·시간을 입력하세요.')
      return
    }
    apiJson<{ id: number }>('/api/attendance-events', {
      method: 'POST',
      body: JSON.stringify({ employee_no: no, event_type: typ, event_date: dt, event_time: tm }),
    })
      .then(() => loadRawEvents())
      .then(() => adminAlert('추가되었습니다.'))
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('raw-edit-btn-update', '원시자료', () => {
    if (!selectedRawEventId) {
      adminAlert('수정할 원시자료 행을 먼저 선택하세요.')
      return
    }
    const no = (document.getElementById('raw-edit-emp-no') as HTMLInputElement | null)?.value?.trim() ?? ''
    const typ = (document.getElementById('raw-edit-type') as HTMLSelectElement | null)?.value ?? 'IN'
    const dt = (document.getElementById('raw-edit-date') as HTMLInputElement | null)?.value ?? ''
    const tm = (document.getElementById('raw-edit-time') as HTMLInputElement | null)?.value ?? ''
    if (!no || !dt || !tm) {
      adminAlert('사번·날짜·시간을 입력하세요.')
      return
    }
    const id = selectedRawEventId
    apiJson(`/api/attendance-events/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ employee_no: no, event_type: typ, event_date: dt, event_time: tm }),
    })
      .then(() => loadRawEvents())
      .then(() => adminAlert('수정되었습니다.'))
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('raw-edit-btn-delete', '원시자료', () => {
    if (!selectedRawEventId) {
      adminAlert('삭제할 원시자료 행을 먼저 선택하세요.')
      return
    }
    const id = selectedRawEventId
    apiJson(`/api/attendance-events/${id}`, { method: 'DELETE' })
      .then(() => {
        clearRawEditSelection()
        return loadRawEvents()
      })
      .then(() => adminAlert('삭제되었습니다.'))
      .catch((err) => adminAlert(String(err)))
  })
}

async function loadRawPanel() {
  initRawToolbarDates()
  await loadRawStaff()
  if (!rawPanelWired) {
    wireRawPanelOnce()
    rawPanelWired = true
  }
  await loadRawEvents()
}

let latestLeavePromotionCampaignId: number | null = null

function lpFmtDt(iso: string | null | undefined): string {
  if (!iso) return '—'
  return iso.slice(0, 16).replace('T', ' ')
}

async function loadLeavePromotionDeptOptions() {
  const sel = document.getElementById('lp-dept') as HTMLSelectElement | null
  if (!sel) return
  const rows = await apiJson<DeptRow[]>('/api/departments')
  const keep = sel.value
  sel.innerHTML = '<option value="">전체</option>'
  for (const d of rows) {
    const o = document.createElement('option')
    o.value = d.name
    o.textContent = d.name
    sel.appendChild(o)
  }
  if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep
}

async function runLeavePromotionSearch(showAlertWhenNoCampaign = false) {
  const tb = document.getElementById('tbody-leave-promotion-targets')
  if (!tb) return

  const campSel = document.getElementById('lp-campaign-select') as HTMLSelectElement | null
  const rawCamp = campSel?.value?.trim() ?? ''
  let id: number | null = null
  if (rawCamp) {
    const p = parseInt(rawCamp, 10)
    if (Number.isFinite(p) && p > 0) id = p
  }
  if (id == null) id = latestLeavePromotionCampaignId
  if (id != null) latestLeavePromotionCampaignId = id

  if (!id) {
    tb.innerHTML =
      '<tr><td colspan="7" class="admin-empty-msg">캠페인을 등록한 뒤 조회하세요.</td></tr>'
    if (showAlertWhenNoCampaign) {
      adminAlert(
        '연차촉진 캠페인이 없습니다. 아래 「촉진 안내 설정」에서 캠페인을 등록한 뒤 다시 조회하세요.',
      )
    }
    return
  }
  tb.innerHTML =
    '<tr><td colspan="7" class="admin-empty-msg">불러오는 중…</td></tr>'
  const yearEl = document.getElementById('lp-year') as HTMLInputElement | null
  const statusEl = document.getElementById('lp-status') as HTMLSelectElement | null
  const year = yearEl?.value?.trim() || String(new Date().getFullYear())
  const status = statusEl?.value?.trim() || ''
  const q = new URLSearchParams({ year })
  if (status) q.set('status', status)
  const rows = await apiJson<LpTargetRow[]>(`/api/leave-promotion/campaigns/${id}/targets?${q.toString()}`)
  const deptSel = document.getElementById('lp-dept') as HTMLSelectElement | null
  const deptFilter = deptSel?.value?.trim() ?? ''
  let filtered = rows
  if (deptFilter) {
    filtered = rows.filter((r) => (r.department_name || '') === deptFilter)
  }
  if (!filtered.length) {
    if (rows.length && deptFilter) {
      tb.innerHTML =
        '<tr><td colspan="7" class="admin-empty-msg">선택한 부서에 해당하는 대상이 없습니다. 부서를 「전체」로 바꿔 조회해 보세요.</td></tr>'
    } else if (!rows.length) {
      if (status === 'signed') {
        tb.innerHTML =
          '<tr><td colspan="7" class="admin-empty-msg">서명완료된 대상이 없습니다. 서명상태를 「전체」로 하거나 다른 캠페인을 선택해 보세요.</td></tr>'
      } else if (status === 'pending') {
        tb.innerHTML =
          '<tr><td colspan="7" class="admin-empty-msg">미서명 대상이 없습니다. (이미 모두 서명했을 수 있습니다.)</td></tr>'
      } else {
        tb.innerHTML =
          '<tr><td colspan="7" class="admin-empty-msg">이 캠페인에 등록된 대상자가 없습니다. 「등록 사원 대상 추가」를 눌렀는지 확인하세요. 모바일 서명은 <strong>최신 캠페인</strong> 기준이므로, 여기서 선택한 캠페인과 같아야 합니다.</td></tr>'
      }
    } else {
      tb.innerHTML =
        '<tr><td colspan="7" class="admin-empty-msg">조건에 맞는 대상이 없습니다.</td></tr>'
    }
    return
  }
  tb.innerHTML = filtered
    .map(
      (r) => `<tr>
      <td>${escapeHtml(r.employee_no)}</td>
      <td>${escapeHtml(r.name)}</td>
      <td>${escapeHtml(r.department_name ?? '')}</td>
      <td>${r.remaining_days != null ? escapeHtml(String(r.remaining_days)) : '—'}</td>
      <td>${escapeHtml(lpFmtDt(r.first_sent_at))}</td>
      <td>${escapeHtml(lpFmtDt(r.second_sent_at))}</td>
      <td>${r.signed_at ? '서명완료' : '미서명'}</td>
    </tr>`,
    )
    .join('')
}

function applyLeavePromotionStats(c: LpCampaignRow | null | undefined): void {
  const stT = document.getElementById('lp-stat-target')
  const stP = document.getElementById('lp-stat-pending')
  const st1 = document.getElementById('lp-stat-first')
  const st2 = document.getElementById('lp-stat-second')
  if (stT) stT.textContent = c ? String(c.target_count) : '0'
  if (stP) stP.textContent = c ? String(Math.max(0, c.target_count - c.signed_count)) : '0'
  if (st1) st1.textContent = c ? String(c.first_sent_count) : '0'
  if (st2) st2.textContent = c ? String(c.second_sent_count) : '0'
}

/**
 * @param preferredCampaignId 방금 생성한 캠페인 id 등, 목록 갱신 후 이 캠페인을 선택할 때 사용
 */
async function refreshLeavePromotionView(preferredCampaignId?: number | null) {
  await loadLeavePromotionDeptOptions()
  const yEl = document.getElementById('lp-year') as HTMLInputElement | null
  if (yEl && !yEl.value?.trim()) {
    yEl.value = String(new Date().getFullYear())
  }
  const campaigns = await apiJson<LpCampaignRow[]>('/api/leave-promotion/campaigns')
  const ids = campaigns.map((x) => x.id)
  const sel = document.getElementById('lp-campaign-select') as HTMLSelectElement | null
  if (sel) {
    sel.innerHTML = ''
    for (const camp of campaigns) {
      const o = document.createElement('option')
      o.value = String(camp.id)
      o.textContent = `#${camp.id} · ${camp.title} (대상 ${camp.target_count}명)`
      sel.appendChild(o)
    }
  }
  let pick: number | null = null
  if (preferredCampaignId != null && ids.includes(preferredCampaignId)) {
    pick = preferredCampaignId
  } else if (latestLeavePromotionCampaignId != null && ids.includes(latestLeavePromotionCampaignId)) {
    pick = latestLeavePromotionCampaignId
  } else if (campaigns[0]) {
    pick = campaigns[0].id
  }
  latestLeavePromotionCampaignId = pick
  if (sel && pick != null) sel.value = String(pick)
  const c = campaigns.find((x) => x.id === pick)
  applyLeavePromotionStats(c ?? null)
  await runLeavePromotionSearch()
}

function wireLeavePromotion() {
  const runSearch = () => {
    void runLeavePromotionSearch(true).catch((e) => adminAlert(String(e)))
  }
  bindButtonById('lp-btn-search', '연차촉진', runSearch)
  document.getElementById('lp-campaign-select')?.addEventListener('change', () => {
    const sel = document.getElementById('lp-campaign-select') as HTMLSelectElement | null
    const v = sel?.value?.trim()
    const id = v ? parseInt(v, 10) : NaN
    if (!Number.isFinite(id)) return
    latestLeavePromotionCampaignId = id
    void (async () => {
      const campaigns = await apiJson<LpCampaignRow[]>('/api/leave-promotion/campaigns')
      const c = campaigns.find((x) => x.id === id)
      applyLeavePromotionStats(c ?? null)
      await runLeavePromotionSearch()
    })().catch((e) => adminAlert(String(e)))
  })
  bindButtonById('lp-btn-campaign-save', '연차촉진', () => {
    const title =
      (document.getElementById('lp-campaign-title') as HTMLInputElement | null)?.value?.trim() ?? ''
    const docVersion =
      (document.getElementById('lp-doc-version') as HTMLInputElement | null)?.value?.trim() || 'v1.0'
    const message = (document.getElementById('lp-message') as HTMLTextAreaElement | null)?.value ?? ''
    if (!title || !message.trim()) {
      adminAlert('제목과 안내 문구를 입력하세요.')
      return
    }
    void apiJson<{ id: number }>('/api/leave-promotion/campaigns', {
      method: 'POST',
      body: JSON.stringify({ title, message, doc_version: docVersion }),
    })
      .then((created) => refreshLeavePromotionView(created.id))
      .then(() =>
        adminAlert(
          '캠페인이 등록되었습니다. 새 캠페인에는 촉진 대상이 비어 있습니다. 「등록 사원 대상 추가」로 넣거나, 이전 캠페인은 위 「캠페인」에서 선택해 확인할 수 있습니다.',
        ),
      )
      .catch((err) => adminAlert(String(err)))
  })
  bindButtonById('lp-btn-add-all-targets', '연차촉진', () => {
    void (async () => {
      const cid = latestLeavePromotionCampaignId
      if (!cid) {
        adminAlert('먼저 캠페인을 등록하세요.')
        return
      }
      const emps = await apiJson<EmpRow[]>('/api/employees')
      const ids = emps.map((e) => e.id)
      if (!ids.length) {
        adminAlert('등록된 사원이 없습니다.')
        return
      }
      await apiJson<{ added: number }>(`/api/leave-promotion/campaigns/${cid}/targets`, {
        method: 'POST',
        body: JSON.stringify({ employee_ids: ids }),
      })
      await refreshLeavePromotionView()
      adminAlert('등록된 사원을 촉진 대상에 반영했습니다.')
    })().catch((e) => adminAlert(String(e)))
  })
  bindButtonById('lp-btn-send-first', '연차촉진', () => {
    void (async () => {
      const cid = latestLeavePromotionCampaignId
      if (!cid) {
        adminAlert('캠페인이 없습니다.')
        return
      }
      await apiJson(`/api/leave-promotion/campaigns/${cid}/send-first`, { method: 'POST' })
      await refreshLeavePromotionView()
      adminAlert('1차 발송 시각이 기록되었습니다.')
    })().catch((e) => adminAlert(String(e)))
  })
  bindButtonById('lp-btn-send-second', '연차촉진', () => {
    void (async () => {
      const cid = latestLeavePromotionCampaignId
      if (!cid) {
        adminAlert('캠페인이 없습니다.')
        return
      }
      await apiJson(`/api/leave-promotion/campaigns/${cid}/send-second`, { method: 'POST' })
      await refreshLeavePromotionView()
      adminAlert('2차 발송 시각이 기록되었습니다.')
    })().catch((e) => adminAlert(String(e)))
  })
  document.getElementById('lp-btn-preview')?.addEventListener('click', () => {
    const title = (document.getElementById('lp-campaign-title') as HTMLInputElement | null)?.value ?? ''
    const message = (document.getElementById('lp-message') as HTMLTextAreaElement | null)?.value ?? ''
    adminAlert(`${title}\n\n${message}`.slice(0, 2000))
  })
}

function wireCrudDept() {
  const tbody = document.getElementById('tbody-dept')
  const codeEl = document.getElementById('dept-code') as HTMLInputElement | null
  const nameEl = document.getElementById('dept-name') as HTMLInputElement | null
  if (!tbody || !codeEl || !nameEl) {
    console.error('[admin] wireCrudDept: DOM 없음', {
      tbody: !!tbody,
      deptCode: !!codeEl,
      deptName: !!nameEl,
    })
    return
  }
  const tb = tbody
  const c = codeEl
  const n = nameEl

  let selected: HTMLTableRowElement | null = null

  function clearSelect() {
    tb.querySelectorAll('tr').forEach((r) => r.classList.remove('is-selected'))
    selected = null
  }

  function fillForm(tr: HTMLTableRowElement) {
    c.value = tr.dataset.code ?? ''
    n.value = tr.dataset.name ?? ''
  }

  function selectRow(tr: HTMLTableRowElement) {
    clearSelect()
    tr.classList.add('is-selected')
    selected = tr
    fillForm(tr)
  }

  async function loadDepartments() {
    const rows = await apiJson<DeptRow[]>('/api/departments')
    tb.innerHTML = ''
    for (const row of rows) {
      const tr = document.createElement('tr')
      tr.tabIndex = 0
      tr.dataset.id = String(row.id)
      tr.dataset.code = row.code
      tr.dataset.name = row.name
      tr.innerHTML = `<td>${escapeHtml(row.code)}</td><td>${escapeHtml(row.name)}</td>`
      tb.appendChild(tr)
    }
    if (!rows.length) {
      const tr = document.createElement('tr')
      tr.innerHTML = '<td colspan="2" class="admin-empty-msg">데이터가 없습니다</td>'
      tb.appendChild(tr)
    }
  }

  tb.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    if (!tr || tr.parentElement !== tb || !tr.dataset.id) return
    selectRow(tr as HTMLTableRowElement)
  })

  bindButtonById('dept-btn-add', '부서 화면', () => {
    const name = n.value.trim()
    if (!name) {
      adminAlert('부서명을 입력하세요.')
      return
    }
    const body = { name }
    apiJson<{ id: number }>('/api/departments', { method: 'POST', body: JSON.stringify(body) })
      .then(() => loadDepartments())
      .then(() => refreshEmployeeDepartmentSelect())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('dept-btn-update', '부서 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('수정할 부서 행을 먼저 선택하세요.')
      return
    }
    const code = c.value.trim()
    const name = n.value.trim()
    if (!code || !name) {
      adminAlert('수정할 행을 선택하고 부서코드·부서명을 확인하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ code, name }),
    })
      .then(() => loadDepartments())
      .then(() => refreshEmployeeDepartmentSelect())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        adminAlert('수정되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('dept-btn-delete', '부서 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('삭제할 부서 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/departments/${id}`, { method: 'DELETE' })
      .then(() => loadDepartments())
      .then(() => refreshEmployeeDepartmentSelect())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        adminAlert('삭제되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  loadDepartments().catch((e) => adminAlert(String(e)))
}

function authBadge(auth: string) {
  const ok = auth === 'O'
  const cls = ok ? 'badge badge-ok' : 'badge badge-muted'
  const label = ok ? 'O' : 'X'
  return `<span class="${cls}" title="${ok ? '인증완료' : '미인증'}">${escapeHtml(label)}</span>`
}

/** 사원 폼 부서 콤보 (`option.value` = 부서명, API `department_name`과 동일) */
async function fillEmployeeDepartmentSelect(
  sel: HTMLSelectElement,
  preserveValue?: string,
): Promise<void> {
  const rows = await apiJson<DeptRow[]>('/api/departments')
  const keep = preserveValue ?? sel.value
  sel.innerHTML = ''
  const opt0 = document.createElement('option')
  opt0.value = ''
  opt0.textContent = '부서 선택'
  sel.appendChild(opt0)
  for (const row of rows) {
    const o = document.createElement('option')
    o.value = row.name
    o.textContent = `${row.code} · ${row.name}`
    sel.appendChild(o)
  }
  if (keep && [...sel.options].some((o) => o.value === keep)) {
    sel.value = keep
  } else {
    sel.value = ''
  }
}

async function refreshEmployeeDepartmentSelect(): Promise<void> {
  const sel = document.getElementById('emp-dept') as HTMLSelectElement | null
  if (!sel) return
  await fillEmployeeDepartmentSelect(sel, sel.value)
}

function wireCrudEmployees() {
  const tbody = document.getElementById('tbody-employees')
  const codeEl = document.getElementById('emp-code') as HTMLInputElement | null
  const nameEl = document.getElementById('emp-name') as HTMLInputElement | null
  const deptEl = document.getElementById('emp-dept') as HTMLSelectElement | null
  const hireEl = document.getElementById('emp-hire') as HTMLInputElement | null
  const baseLeaveEl = document.getElementById('emp-base-leave') as HTMLInputElement | null
  const remainLeaveEl = document.getElementById('emp-remain-leave') as HTMLInputElement | null
  const usedLeaveEl = document.getElementById('emp-used-leave') as HTMLInputElement | null
  const statusEl = document.getElementById('emp-status') as HTMLSelectElement | null
  if (!tbody || !codeEl || !nameEl || !deptEl || !hireEl || !baseLeaveEl || !remainLeaveEl || !usedLeaveEl || !statusEl) {
    console.error('[admin] wireCrudEmployees: DOM 없음')
    return
  }
  const tb = tbody
  const c = codeEl
  const n = nameEl
  const d = deptEl
  const h = hireEl
  const bl = baseLeaveEl
  const rl = remainLeaveEl
  const ul = usedLeaveEl
  const st = statusEl

  const syncBaseLeave = () => {
    bl.value = calcBaseAnnualLeaveByHireDate(h.value)
  }
  h.addEventListener('change', syncBaseLeave)

  let selected: HTMLTableRowElement | null = null

  function badgeFor(status: string) {
    let cls = 'badge badge-muted'
    if (status === '재직') cls = 'badge badge-ok'
    else if (status === '휴직') cls = 'badge badge-warn'
    return `<span class="${cls}">${escapeHtml(status)}</span>`
  }

  function clearSelect() {
    tb.querySelectorAll('tr').forEach((r) => r.classList.remove('is-selected'))
    selected = null
  }

  function fillForm(tr: HTMLTableRowElement) {
    c.value = tr.dataset.code ?? ''
    n.value = tr.dataset.name ?? ''
    d.value = tr.dataset.dept ?? ''
    h.value = tr.dataset.hire ?? ''
    syncBaseLeave()
    rl.value = '…'
    ul.value = '…'
    st.value = tr.dataset.status ?? '재직'
  }

  async function refreshEmpAnnualLine(empId: string) {
    if (!ul || !rl || !bl) return
    const y = new Date().getFullYear()
    try {
      const data = await apiJson<{
        base_days: number
        used_days: number
        remaining_days: number
        leave_code: string
        leave_name: string
      }>(`/api/employee-leaves/employee/${empId}/annual-line?year=${y}`)
      bl.value = String(data.base_days)
      ul.value = String(data.used_days)
      rl.value = String(data.remaining_days)
    } catch {
      syncBaseLeave()
      ul.value = '—'
      rl.value = '—'
    }
  }

  function selectRow(tr: HTMLTableRowElement) {
    clearSelect()
    tr.classList.add('is-selected')
    selected = tr
    fillForm(tr)
    const eid = tr.dataset.id
    if (eid) void refreshEmpAnnualLine(eid)
  }

  async function loadEmployees() {
    const selectedId = selected?.dataset.id ?? null
    const rows = await apiJson<EmpRow[]>('/api/employees')
    tb.innerHTML = ''
    for (const row of rows) {
      const auth = row.auth_status === 'O' ? 'O' : 'X'
      const tr = document.createElement('tr')
      tr.tabIndex = 0
      tr.dataset.id = String(row.id)
      tr.dataset.code = row.employee_no
      tr.dataset.name = row.name
      tr.dataset.dept = row.department_name ?? ''
      tr.dataset.hire = hireInputValue(row.hire_date)
      tr.dataset.status = row.status
      tr.dataset.auth = auth
      tr.innerHTML = `<td>${escapeHtml(row.employee_no)}</td><td>${escapeHtml(row.name)}</td><td>${escapeHtml(
        row.department_name ?? '',
      )}</td><td>${escapeHtml(hireInputValue(row.hire_date))}</td><td>${badgeFor(row.status)}</td><td>${authBadge(
        auth,
      )}</td>`
      tb.appendChild(tr)
    }
    if (!rows.length) {
      const tr = document.createElement('tr')
      tr.innerHTML = '<td colspan="6" class="admin-empty-msg">데이터가 없습니다</td>'
      tb.appendChild(tr)
    }
    if (selectedId) {
      const tr = tb.querySelector<HTMLTableRowElement>(`tr[data-id="${selectedId}"]`)
      if (tr) selectRow(tr)
    }
  }

  tb.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    if (!tr || tr.parentElement !== tb || !tr.dataset.id) return
    selectRow(tr as HTMLTableRowElement)
  })

  bindButtonById('emp-btn-add', '사원 화면', () => {
    const employee_no = c.value.trim()
    const name = n.value.trim()
    const department_name = d.value.trim()
    const hire_date = h.value
    const status = st.value
    if (!employee_no || !name || !department_name || !hire_date) {
      adminAlert('사번, 이름, 부서, 입사일을 모두 입력하세요.')
      return
    }
    apiJson<{ id: number }>('/api/employees', {
      method: 'POST',
      body: JSON.stringify({ employee_no, name, department_name, hire_date, status }),
    })
      .then(() => loadEmployees())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        d.value = ''
        h.value = ''
        bl.value = ''
        rl.value = '0'
        ul.value = '0'
        st.value = '재직'
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('emp-btn-update', '사원 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('수정할 사원 행을 먼저 선택하세요.')
      return
    }
    const employee_no = c.value.trim()
    const name = n.value.trim()
    const department_name = d.value.trim()
    const hire_date = h.value
    const status = st.value
    if (!employee_no || !name || !department_name || !hire_date) {
      adminAlert('사번, 이름, 부서, 입사일을 모두 입력하세요.')
      return
    }
    const id = selected.dataset.id
    const y = new Date().getFullYear()
    apiJson(`/api/employees/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ employee_no, name, department_name, hire_date, status }),
    })
      .then(async () => {
        const usedNum = parseFloat(ul.value)
        if (Number.isFinite(usedNum)) {
          await apiJson(`/api/employee-leaves/employee/${id}/annual-line`, {
            method: 'PUT',
            body: JSON.stringify({ year: y, used_days: usedNum }),
          })
        }
      })
      .then(() => loadEmployees())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        d.value = ''
        h.value = ''
        bl.value = ''
        rl.value = '0'
        ul.value = '0'
        st.value = '재직'
        adminAlert('수정되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('emp-btn-delete', '사원 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('삭제할 사원 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/employees/${id}`, { method: 'DELETE' })
      .then(() => loadEmployees())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        d.value = ''
        h.value = ''
        bl.value = ''
        rl.value = '0'
        ul.value = '0'
        st.value = '재직'
        adminAlert('삭제되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('emp-btn-revoke-auth', '사원 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('인증을 취소할 사원 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/employees/${id}/revoke-auth`, { method: 'POST' })
      .then(() => loadEmployees())
      .then(() => {
        const tr = tb.querySelector<HTMLTableRowElement>(`tr[data-id="${id}"]`)
        if (tr) selectRow(tr)
        adminAlert('인증이 취소되었습니다. 모바일에서 비밀번호를 다시 설정할 수 있습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  fillEmployeeDepartmentSelect(d)
    .then(() => loadEmployees())
    .catch((e) => adminAlert(String(e)))

  employeeRealtimeLoad = loadEmployees
}

function wireCrudLeave() {
  const tbody = document.getElementById('tbody-leave')
  const codeEl = document.getElementById('leave-code') as HTMLInputElement | null
  const nameEl = document.getElementById('leave-name') as HTMLInputElement | null
  if (!tbody || !codeEl || !nameEl) {
    console.error('[admin] wireCrudLeave: DOM 없음')
    return
  }
  const tb = tbody
  const c = codeEl
  const n = nameEl

  let selected: HTMLTableRowElement | null = null

  function clearSelect() {
    tb.querySelectorAll('tr').forEach((r) => r.classList.remove('is-selected'))
    selected = null
  }

  function fillForm(tr: HTMLTableRowElement) {
    c.value = tr.dataset.code ?? ''
    n.value = tr.dataset.name ?? ''
  }

  function selectRow(tr: HTMLTableRowElement) {
    clearSelect()
    tr.classList.add('is-selected')
    selected = tr
    fillForm(tr)
  }

  async function loadLeaveCodes() {
    const rows = await apiJson<LeaveRow[]>('/api/leave-codes')
    tb.innerHTML = ''
    for (const row of rows) {
      const tr = document.createElement('tr')
      tr.tabIndex = 0
      tr.dataset.id = String(row.id)
      tr.dataset.code = row.code
      tr.dataset.name = row.name
      tr.innerHTML = `<td>${escapeHtml(row.code)}</td><td>${escapeHtml(row.name)}</td>`
      tb.appendChild(tr)
    }
    if (!rows.length) {
      const tr = document.createElement('tr')
      tr.innerHTML = '<td colspan="2" class="admin-empty-msg">데이터가 없습니다</td>'
      tb.appendChild(tr)
    }
  }

  tb.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    if (!tr || tr.parentElement !== tb || !tr.dataset.id) return
    selectRow(tr as HTMLTableRowElement)
  })

  bindButtonById('leave-btn-add', '휴가코드 화면', () => {
    const name = n.value.trim()
    if (!name) {
      adminAlert('명칭을 입력하세요.')
      return
    }
    const body = { name }
    apiJson<{ id: number }>('/api/leave-codes', { method: 'POST', body: JSON.stringify(body) })
      .then(() => loadLeaveCodes())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('leave-btn-update', '휴가코드 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('수정할 휴가코드 행을 먼저 선택하세요.')
      return
    }
    const code = c.value.trim()
    const name = n.value.trim()
    if (!code || !name) {
      adminAlert('수정할 행을 선택하고 코드·명칭을 확인하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/leave-codes/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ code, name }),
    })
      .then(() => loadLeaveCodes())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        adminAlert('수정되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('leave-btn-delete', '휴가코드 화면', () => {
    if (!selected?.dataset.id) {
      adminAlert('삭제할 휴가코드 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/leave-codes/${id}`, { method: 'DELETE' })
      .then(() => loadLeaveCodes())
      .then(() => {
        clearSelect()
        c.value = ''
        n.value = ''
        adminAlert('삭제되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  loadLeaveCodes().catch((e) => adminAlert(String(e)))
}

function wireCrudWorkShift() {
  const tbody = document.getElementById('tbody-work-shift')
  const nameEl = document.getElementById('work-shift-name') as HTMLInputElement | null
  const inEl = document.getElementById('work-shift-in') as HTMLInputElement | null
  const outEl = document.getElementById('work-shift-out') as HTMLInputElement | null
  if (!tbody || !nameEl || !inEl || !outEl) {
    console.error('[admin] wireCrudWorkShift: DOM 없음')
    return
  }
  const tb = tbody
  const n = nameEl
  const cin = inEl
  const cout = outEl
  let selected: HTMLTableRowElement | null = null

  function clearSelect() {
    tb.querySelectorAll('tr').forEach((r) => r.classList.remove('is-selected'))
    selected = null
  }

  function fillForm(tr: HTMLTableRowElement) {
    n.value = tr.dataset.name ?? ''
    cin.value = normalizeTimeInput(tr.dataset.clockIn ?? '')
    cout.value = normalizeTimeInput(tr.dataset.clockOut ?? '')
  }

  function selectRow(tr: HTMLTableRowElement) {
    clearSelect()
    tr.classList.add('is-selected')
    selected = tr
    fillForm(tr)
  }

  async function loadWorkShifts() {
    const rows = await apiJson<WorkShiftRow[]>('/api/work-shifts')
    tb.innerHTML = ''
    let idx = 0
    for (const row of rows) {
      idx += 1
      const tr = document.createElement('tr')
      tr.tabIndex = 0
      tr.dataset.id = String(row.id)
      tr.dataset.name = row.name
      tr.dataset.clockIn = row.clock_in
      tr.dataset.clockOut = row.clock_out
      tr.innerHTML = `<td>${idx}</td><td>${escapeHtml(row.name)}</td><td>${escapeHtml(row.clock_in)}</td><td>${escapeHtml(row.clock_out)}</td>`
      tb.appendChild(tr)
    }
    if (!rows.length) {
      const tr = document.createElement('tr')
      tr.innerHTML = '<td colspan="4" class="admin-empty-msg">데이터가 없습니다</td>'
      tb.appendChild(tr)
    }
  }

  tb.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    if (!tr || tr.parentElement !== tb || !tr.dataset.id) return
    selectRow(tr as HTMLTableRowElement)
  })

  bindButtonById('work-shift-btn-add', '근무시간 관리', () => {
    const name = n.value.trim()
    const clock_in = cin.value
    const clock_out = cout.value
    if (!name) {
      adminAlert('근태명을 입력하세요.')
      return
    }
    if (!clock_in || !clock_out) {
      adminAlert('출근·퇴근 시간을 선택하세요.')
      return
    }
    apiJson<{ id: number }>('/api/work-shifts', {
      method: 'POST',
      body: JSON.stringify({ name, clock_in, clock_out }),
    })
      .then(() => loadWorkShifts())
      .then(() => {
        clearSelect()
        n.value = ''
        cin.value = ''
        cout.value = ''
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('work-shift-btn-update', '근무시간 관리', () => {
    if (!selected?.dataset.id) {
      adminAlert('수정할 행을 먼저 선택하세요.')
      return
    }
    const name = n.value.trim()
    const clock_in = cin.value
    const clock_out = cout.value
    if (!name || !clock_in || !clock_out) {
      adminAlert('근태명·출근·퇴근을 모두 입력하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/work-shifts/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, clock_in, clock_out }),
    })
      .then(() => loadWorkShifts())
      .then(() => {
        clearSelect()
        n.value = ''
        cin.value = ''
        cout.value = ''
        adminAlert('수정되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('work-shift-btn-delete', '근무시간 관리', () => {
    if (!selected?.dataset.id) {
      adminAlert('삭제할 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.id
    apiJson(`/api/work-shifts/${id}`, { method: 'DELETE' })
      .then(() => loadWorkShifts())
      .then(() => {
        clearSelect()
        n.value = ''
        cin.value = ''
        cout.value = ''
        adminAlert('삭제되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  loadWorkShifts().catch((e) => adminAlert(String(e)))
}

/** API HH:MM → input[type=time] 값 (HH:MM) */
function normalizeTimeInput(s: string): string {
  const t = s.trim()
  if (/^\d{1,2}:\d{2}$/.test(t)) {
    const [h, m] = t.split(':')
    return `${h.padStart(2, '0')}:${m}`
  }
  if (/^\d{1,2}:\d{2}:\d{2}$/.test(t)) {
    return `${t.slice(0, 2)}:${t.slice(3, 5)}`
  }
  return t.slice(0, 5)
}

function initLeaveEmpToolbarDates() {
  const from = document.getElementById('leave-emp-date-from') as HTMLInputElement | null
  const to = document.getElementById('leave-emp-date-to') as HTMLInputElement | null
  if (!from || !to) return
  if (!from.value || !to.value) {
    const y = new Date().getFullYear()
    from.value = `${y}-01-01`
    to.value = `${y}-12-31`
  }
}

function leaveEmpSearchQuery(): string {
  const fromEl = document.getElementById('leave-emp-date-from') as HTMLInputElement | null
  const toEl = document.getElementById('leave-emp-date-to') as HTMLInputElement | null
  const qEl = document.getElementById('leave-emp-line-q') as HTMLInputElement | null
  const p = new URLSearchParams()
  if (fromEl?.value) p.set('date_from', fromEl.value)
  if (toEl?.value) p.set('date_to', toEl.value)
  const q = qEl?.value?.trim()
  if (q) p.set('q', q)
  const s = p.toString()
  return s ? `?${s}` : ''
}

let _leaveEmpLoadTable: (() => Promise<void>) | null = null

async function refreshLeaveEmpView() {
  initLeaveEmpToolbarDates()
  if (_leaveEmpLoadTable) await _leaveEmpLoadTable()
}

function wireLeaveEmp() {
  const tbody = document.getElementById('tbody-leave-emp')
  const sel = document.getElementById('leave-emp-code-select') as HTMLSelectElement | null
  const noEl = document.getElementById('leave-emp-no') as HTMLInputElement | null
  const nameEl = document.getElementById('leave-emp-name') as HTMLInputElement | null
  const startEl = document.getElementById('leave-emp-start') as HTMLInputElement | null
  const endEl = document.getElementById('leave-emp-end') as HTMLInputElement | null
  if (!tbody || !sel || !noEl || !nameEl || !startEl || !endEl) {
    console.error('[admin] wireLeaveEmp: DOM 없음')
    return
  }
  const tb = tbody
  const leaveSel = sel
  const empNoEl = noEl
  const empNameEl = nameEl
  const startInp = startEl
  const endInp = endEl
  let selected: HTMLTableRowElement | null = null

  function clearSelect() {
    tb.querySelectorAll('tr').forEach((r) => r.classList.remove('is-selected'))
    selected = null
  }

  function clearForm() {
    empNoEl.value = ''
    empNameEl.value = ''
    startInp.value = ''
    endInp.value = ''
    if (leaveSel.options.length) leaveSel.selectedIndex = 0
  }

  function fillFormFromRow(tr: HTMLTableRowElement) {
    empNoEl.value = tr.dataset.employeeNo ?? ''
    empNameEl.value = tr.dataset.employeeName ?? ''
    const lc = tr.dataset.leaveCodeId ?? ''
    leaveSel.value = lc
    const sd = tr.dataset.startDate ?? ''
    const ed = tr.dataset.endDate ?? ''
    startInp.value = sd.length >= 10 ? sd.slice(0, 10) : sd
    endInp.value = ed.length >= 10 ? ed.slice(0, 10) : ed
  }

  function selectRow(tr: HTMLTableRowElement) {
    clearSelect()
    tr.classList.add('is-selected')
    selected = tr
    fillFormFromRow(tr)
  }

  async function loadLeaveCodeOptions() {
    const v = leaveSel.value
    leaveSel.innerHTML = ''
    const rows = await apiJson<LeaveRow[]>('/api/leave-codes')
    for (const row of rows) {
      const o = document.createElement('option')
      o.value = String(row.id)
      o.textContent = `${row.code} · ${row.name}`
      leaveSel.appendChild(o)
    }
    if (v && [...leaveSel.options].some((o) => o.value === v)) leaveSel.value = v
  }

  async function loadLeaveEmpTable() {
    const path = `/api/employee-leaves${leaveEmpSearchQuery()}`
    const rows = await apiJson<EmpLeaveListRow[]>(path)
    const selId = selected?.dataset.recordId
    tb.innerHTML = ''
    for (const row of rows) {
      const tr = document.createElement('tr')
      tr.tabIndex = 0
      tr.dataset.recordId = String(row.id)
      tr.dataset.employeeNo = row.employee_no
      tr.dataset.employeeName = row.name
      tr.dataset.leaveCodeId = String(row.leave_code_id)
      tr.dataset.startDate = row.start_date
      tr.dataset.endDate = row.end_date
      const content = `${row.leave_name}`
      const rem = row.remaining_days == null ? '—' : String(row.remaining_days)
      tr.innerHTML = `<td>${escapeHtml(row.employee_no)}</td><td>${escapeHtml(row.name)}</td><td>${escapeHtml(content)}</td><td>${escapeHtml(row.start_date.slice(0, 10))}</td><td>${escapeHtml(row.end_date.slice(0, 10))}</td><td>${row.total_days}</td><td>${row.work_days}</td><td>${row.cumulative_work_days}</td><td>${escapeHtml(rem)}</td>`
      tb.appendChild(tr)
    }
    if (!rows.length) {
      const tr = document.createElement('tr')
      tr.innerHTML = '<td colspan="9" class="admin-empty-msg">조건에 맞는 데이터가 없습니다</td>'
      tb.appendChild(tr)
    }
    clearSelect()
    if (selId) {
      const again = tb.querySelector<HTMLTableRowElement>(`tr[data-record-id="${selId}"]`)
      if (again) selectRow(again)
    }
  }

  _leaveEmpLoadTable = () => loadLeaveEmpTable()

  tb.addEventListener('click', (e) => {
    const el = clickTargetElement(e)
    const tr = el?.closest('tr')
    if (!tr || tr.parentElement !== tb || !tr.dataset.recordId) return
    selectRow(tr as HTMLTableRowElement)
  })

  empNoEl.addEventListener('blur', () => {
    const no = empNoEl.value.trim()
    if (!no) {
      empNameEl.value = ''
      return
    }
    apiJson<{ name: string }>(`/api/employees/by-number/${encodeURIComponent(no)}`)
      .then((r) => {
        empNameEl.value = r.name
      })
      .catch(() => {
        empNameEl.value = ''
      })
  })

  bindButtonById('leave-emp-btn-search', '개인별 휴가', () => {
    loadLeaveEmpTable().catch((err) => adminAlert(String(err)))
  })

  bindButtonById('leave-emp-btn-save', '개인별 휴가', () => {
    const employee_no = empNoEl.value.trim()
    const leave_code_id = Number(leaveSel.value)
    const start_date = startInp.value
    const end_date = endInp.value
    if (!employee_no) {
      adminAlert('사번을 입력하세요.')
      return
    }
    if (!leave_code_id) {
      adminAlert('휴가 종류를 선택하세요.')
      return
    }
    if (!start_date || !end_date) {
      adminAlert('휴가 시작일·종료일을 선택하세요.')
      return
    }
    apiJson<{ id: number }>('/api/employee-leaves', {
      method: 'POST',
      body: JSON.stringify({ employee_no, leave_code_id, start_date, end_date }),
    })
      .then(() => loadLeaveEmpTable())
      .then(() => {
        clearSelect()
        clearForm()
        adminAlert('저장되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('leave-emp-btn-update', '개인별 휴가', () => {
    if (!selected?.dataset.recordId) {
      adminAlert('수정할 행을 먼저 선택하세요.')
      return
    }
    const employee_no = empNoEl.value.trim()
    const leave_code_id = Number(leaveSel.value)
    const start_date = startInp.value
    const end_date = endInp.value
    if (!employee_no || !start_date || !end_date || !leave_code_id) {
      adminAlert('사번·휴가·기간을 확인하세요.')
      return
    }
    const id = selected.dataset.recordId
    apiJson(`/api/employee-leaves/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ employee_no, leave_code_id, start_date, end_date }),
    })
      .then(() => loadLeaveEmpTable())
      .then(() => {
        const tr = tb.querySelector<HTMLTableRowElement>(`tr[data-record-id="${id}"]`)
        if (tr) selectRow(tr)
        adminAlert('수정되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  bindButtonById('leave-emp-btn-delete', '개인별 휴가', () => {
    if (!selected?.dataset.recordId) {
      adminAlert('삭제할 행을 먼저 선택하세요.')
      return
    }
    const id = selected.dataset.recordId
    apiJson(`/api/employee-leaves/${id}`, { method: 'DELETE' })
      .then(() => loadLeaveEmpTable())
      .then(() => {
        clearSelect()
        clearForm()
        adminAlert('삭제되었습니다.')
      })
      .catch((err) => adminAlert(String(err)))
  })

  initLeaveEmpToolbarDates()
  loadLeaveCodeOptions()
    .then(() => loadLeaveEmpTable())
    .catch((e) => adminAlert(String(e)))
}

wireCrudDept()
wireCrudEmployees()
wireCrudLeave()
wireCrudWorkShift()
wireLeavePromotion()
wireLeaveEmp()
initRawToolbarDates()
startDashboardAutoRefresh()
bindButtonById('admin-settings-save', '관리자 설정', () => {
  const id = (document.getElementById('admin-login-id') as HTMLInputElement | null)?.value?.trim() ?? ''
  const current = (document.getElementById('admin-current-pw') as HTMLInputElement | null)?.value ?? ''
  const next = (document.getElementById('admin-new-pw') as HTMLInputElement | null)?.value ?? ''
  const next2 = (document.getElementById('admin-new-pw2') as HTMLInputElement | null)?.value ?? ''
  if (!id || !current || !next || !next2) {
    adminAlert('아이디/현재 비밀번호/새 비밀번호를 모두 입력하세요.')
    return
  }
  if (next !== next2) {
    adminAlert('새 비밀번호와 확인이 일치하지 않습니다.')
    return
  }
  adminAlert('관리자 인증(JWT) 백엔드 연동 전 UI 저장 검증만 완료되었습니다.')
})

document.addEventListener('visibilitychange', () => {
  const activeView = document.querySelector('.admin-view.is-active')?.getAttribute('data-view')
  if (document.hidden) {
    stopDashboardAutoRefresh()
    stopEmployeeAutoRefresh()
    return
  }
  if (activeView === 'dashboard') {
    startDashboardAutoRefresh()
  }
  if (activeView === 'employees') {
    startEmployeeAutoRefresh()
  }
})
