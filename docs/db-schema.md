# DB 스키마 (MariaDB · `attend`)

## 초기 테이블

| 테이블 | 용도 |
|--------|------|
| `departments` | 부서코드·부서명 |
| `employees` | 사번·성명·부서 FK·입사일·상태 |
| `leave_codes` | 휴가 코드·명칭 |
| `attendance_events` | 출퇴근 원시 이벤트 (출근/퇴근, 시각·출처·단말) |

`sql/002_*.sql`, `sql/003_*.sql` 적용 시 추가되는 테이블 예:

| 테이블 | 용도 |
|--------|------|
| `employee_leave_records` | 사원별 휴가 사용 기간 |
| `employee_leave_quotas` | 사원·휴가코드·연도별 부여 일수(잔여 계산용) |
| `work_shift_types` | 근무시간 관리: 근태명·출근 시각·퇴근 시각(하루 안의 TIME) |

시각 컬럼의 **비즈니스 의미는 KST** (`docs/korea-time-and-infrastructure.md`).

---

## 근무시간 유형(`work_shift_types`)과 야근·심야(자정 넘김)

관리 화면에는 **날짜 없이** `clock_in`, `clock_out`만 저장한다.  
일반 근무(당일 퇴근)는 출근 시각 &lt; 퇴근 시각으로 해석하면 된다.

**야근조·심야조**처럼 **퇴근이 다음날 아침**인 경우는 도메인 상 다음과 같다.

- 예: 당일 22:00 출근 → **익일** 06:00 퇴근.
- DB에는 `clock_in = 22:00`, `clock_out = 06:00`처럼만 있어도 되지만, **비교·집계 코드에서는** 같은 달력날만 보면 `clock_out < clock_in`처럼 보이므로, 이 경우 **퇴근 시각은 “출근일의 다음날 KST”**에 속한 시각으로 간주해야 한다.
- 실제 출퇴근 원시 기록(`attendance_events`)은 **날짜+시각(또는 타임스탬프)**이 있으므로, 지각·근무 구간 계산 시 위 규칙으로 **기대 퇴근 순간**을 잡는다.

향후 필요하면 `work_shift_types`에 **`spans_midnight`(자정 넘김 여부)** 같은 플래그를 두어, 애매한 구간(당일 일찍 퇴근 vs 익일 새벽 퇴근)을 명시적으로 구분할 수 있다. (현재 스키마에는 없음 — 구현 시 설계 항목.)

## 적용 방법

### 1) 스크립트 (권장, MariaDB 정식 커넥터)

프로젝트 루트에서 `.env` 를 읽고 `sql/001_init.sql` 을 실행합니다.

```bash
`cd client` 후 `npm run db:schema`
```

또는:

```bash
python scripts/apply_schema.py
```

(`pip install -r backend/requirements.txt` 로 `mariadb`, `python-dotenv` 가 있어야 합니다.)

### 2) CLI 클라이언트

MariaDB를 설치하면 보통 **`mariadb`** 또는 호환용 **`mysql`** 이 제공됩니다.

```bash
mariadb -u attend -p attend < sql/001_init.sql
```

`mariadb` 가 없으면 `mysql` 로 동일하게 시도합니다.

적용 후 `SHOW TABLES;` 로 `departments`, `employees`, `leave_codes`, `attendance_events` 가 보이면 됩니다.

## Python API 쪽 연결

FastAPI 백엔드는 **MariaDB 공식 Connector/Python** (`pip install mariadb`, 패키지 이름 `mariadb`)으로 접속합니다. 이전에 문서에 `mysql`만 적혀 있었다면, 그건 **CLI 도구 이름**을 가리킨 것이지 PyMySQL 드라이버를 쓰자는 뜻이 아닙니다.
