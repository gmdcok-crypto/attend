# Railway 배포 참조

이 문서는 **Railway에 attend 백엔드·DB를 올릴 때** 설정과 주의사항을 정리한 것이다. 이후 작업·트러블슈팅 시 여기를 먼저 본다.

## 저장소·프로젝트

- **GitHub**: `https://github.com/gmdcok-crypto/attend`
- **Railway 프로젝트 이름**: **`gs_attend`** (이 레포 백엔드·DB를 묶는 프로젝트)
- 한 프로젝트 안에 **DB 서비스 + Web(API) 서비스**를 둔다.

레포 루트에 **`railway.toml`** (`builder = NIXPACKS`) + **`nixpacks.toml`** 으로 **Nixpacks만** 쓴다. **Dockerfile·Railpack 자동 Docker 빌드는 사용하지 않는다** (레포에 `Dockerfile` 없음).

**Railway 대시보드**에서도 한 번 확인한다: 해당 서비스 **Settings → Build → Builder** 가 **Nixpacks** 인지 ( **Dockerfile** / **Railpack** 이 아닌지 ). UI가 Railpack이면 로그에 `COPY . /app` 같은 Docker 단계가 나올 수 있다.

**`buildCommand`** 는 `pip install -r requirements.txt` 만 실행해, 루트의 `package.json` 때문에 **`npm run build`(Vite)** 가 기본 실행되지 않게 한다. 시작은 **`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`**. 루트 **`requirements.txt`** 는 `backend/requirements.txt` 와 동일 내용을 유지한다.

프론트 정적 빌드(`npm run build`)는 **로컬·CI·별도 Static 서비스**에서 수행한다. Railway API 서비스에서 `npm run build`가 호출되는 예외 상황을 대비해 **`scripts/build.mjs`** 는 Railway 환경 변수가 있으면 **즉시 종료(스킵)** 한다.

## 서비스 구성(권장) — 프로젝트 `gs_attend`

1. **Database**: MySQL/MariaDB 추가 → `MYSQL_DATABASE` / 스키마 이름 **`gs_attend`** (HeidiSQL에서 빈 DB로 만들어 둔 것과 동일).
2. **Web Service**: **GitHub** `gmdcok-crypto/attend` 연결, 브랜치 **`main`**, **Root directory 비움(저장소 루트)**.
3. Web Service **Variables**에 `DB_*`, `JWT_SECRET` 등 설정(아래 표).
4. **Deploy** — Nixpacks가 `pip install` 후 `deploy.startCommand` 로 API를 띄운다.

## DB 연결 — 반드시 사설(프라이빗) 엔드포인트

Railway는 DB에 대해 **공개 URL**(`MYSQL_PUBLIC_URL`, `RAILWAY_TCP_PROXY_DOMAIN` 등)과 **프로젝트 내부 통신용 주소**를 함께 제공한다.

- **백엔드(FastAPI)가 Railway에 올라가 있고, DB도 같은 Railway 프로젝트 안에 있을 때**  
  → API → DB 연결에는 **`MYSQL_PUBLIC_URL`을 쓰지 않는다.**  
  → **내부/프라이빗 호스트**를 사용한다 (Railway DB 서비스의 **Variables** 또는 **Connect** 탭에 안내된 값).

이유: 공개 프록시로 붙으면 **egress(나가는 트래픽) 요금**이 붙을 수 있고, Railway가 경고를 띄운다. 같은 프로젝트 내 서비스 간 통신은 **사설 네트워크**가 맞다.

- **로컬 PC에서만** Railway DB에 직접 접속해 마이그레이션·디버깅할 때는 공개 URL이 필요할 수 있다 (이 경우만).

### DB 이름 `gs_attend` 맞추기

Railway **MySQL/MariaDB 서비스**에는 보통 `MYSQL_DATABASE`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLHOST`(또는 `PGHOST`가 아닌 MySQL용 호스트)·`MYSQLPORT` 등이 자동으로 생긴다.

- **`MYSQL_DATABASE`**: MySQL 안에서 **실제로 쓸 스키마(데이터베이스) 이름**이다. 이 프로젝트에서는 **`gs_attend`** 로 통일하는 것을 권장한다.
  - 플러그인 생성 시 이름을 고를 수 있으면 **`gs_attend`** 로 두거나,
  - 이미 다른 이름(`railway` 등)으로 만들어졌다면: MySQL에 `gs_attend` 데이터베이스를 추가로 만들고(`CREATE DATABASE gs_attend ...`), **`MYSQL_DATABASE`를 `gs_attend`로 바꿀 수 있는지** Railway UI를 확인하거나, 앱 쪽만 `DB_NAME`을 실제 존재하는 DB 이름과 맞춘다.

앱 코드는 `backend/database.py` 기준으로 **`MYSQL_*`를 직접 읽지 않는다.** 반드시 아래 **`DB_*`** 를 **API(웹) 서비스** Variables에 넣는다. 값은 Railway DB가 뿌려 주는 것과 **같은 DB를 가리키면** 된다.

| 앱이 기대하는 변수 (API 서비스) | 설명 |
|-------------------|------|
| `DB_HOST` | DB 호스트 (**프라이빗** 쪽 값) |
| `DB_PORT` | 보통 `3306` (또는 DB 서비스가 준 값) |
| `DB_USER` | DB 사용자 (`MYSQLUSER`와 동일하게) |
| `DB_PASSWORD` | DB 비밀번호 (`MYSQLPASSWORD`와 동일하게) |
| `DB_NAME` | **`gs_attend`** — `MYSQL_DATABASE`와 **반드시 동일한 데이터베이스 이름**이어야 한다. |

즉, **`MYSQL_DATABASE=gs_attend`** 이고 **`DB_NAME=gs_attend`** 이면 이름은 맞다. 한쪽만 다르면 앱이 다른 DB를 보거나 접속 오류가 난다.

추가(운영 권장):

| 변수 | 설명 |
|------|------|
| `JWT_SECRET` | 모바일 JWT 서명용. 강한 임의 문자열. |
| `KIOSK_QR_SECRET` | 키오스크 QR HMAC. 없으면 코드상 `JWT_SECRET` 등으로 대체 로직이 있을 수 있음 — 운영에서는 분리 권장. |

## 빌드·실행 명령 (API 서비스)

- **Install / Start**: `railway.toml` 의 `buildCommand` + `startCommand` (로컬 API는 `npm run dev:api`).

`PORT`는 Railway가 주입한다. 로컬은 `npm run dev:api`와 다르게 **0.0.0.0** 바인딩이 필요하다.

## 스키마·데이터

- 최초 1회: 로컬 또는 Railway 셸에서 `DB_*`가 Railway DB를 가리키도록 한 뒤 `python scripts/apply_schema.py` 등으로 스키마 반영.
- **`DB_NAME` / `MYSQL_DATABASE` 둘 다 `gs_attend`** 인지 확인한 뒤 스키마를 넣는다.

## 헬스 체크

- `GET /api/health`
- DB까지 확인: `GET /api/db/ping` (환경 변수·방화벽이 맞으면)

## 프론트(Vite)

- `npm run build` 결과는 `dist/`. API와 **도메인을 같이 쓰려면** 정적 파일 서빙 또는 별도 Static 호스팅·CDN을 이후 단계에서 결정한다.
- 개발 시에는 Vite가 `/api`를 프록시하므로, 배포 후에는 프론트의 API 베이스 URL을 **Railway API 공개 URL**로 맞춰야 한다 (`vite.config`의 `import.meta.env` 등으로 분리하는 방식이 일반적).

## 작업 시 체크리스트

- [ ] API 서비스의 `DB_*`가 **프라이빗 DB 엔드포인트**를 가리키는가?
- [ ] **`MYSQL_DATABASE`와 `DB_NAME`이 둘 다 `gs_attend`(또는 동일한 DB 이름)인가?**
- [ ] `JWT_SECRET`(및 QR용 시크릿)이 운영 값으로 설정되었는가?
- [ ] 배포 후 `/api/health`, `/api/db/ping` 응답 확인
- [ ] GitHub 푸시 시 자동 배포를 쓰는 경우, 연결 브랜치가 `main`인지 확인

## 관련 문서

- `docs/backend-fastapi.md` — 로컬 실행·Uvicorn
- `docs/db-schema.md` — 스키마 개요
