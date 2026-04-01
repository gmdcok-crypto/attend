# 백엔드 — FastAPI

Node(Express) 대신 **FastAPI + Uvicorn**으로 API를 통일했다.

## 준비

```bash
python -m pip install -r backend/requirements.txt
```

(권장) 가상환경: `python -m venv .venv` 후 활성화하고 위 `pip install` 실행.

## 실행

`client` 디렉터리에서:

```bash
cd client
npm run dev:api
```

- API: `http://127.0.0.1:8000`
- 연결 확인: `GET http://127.0.0.1:8000/api/db/ping`
- 문서: `http://127.0.0.1:8000/docs` (Swagger UI)

프론트(Vite)는 `client/vite.config.ts`에서 `/api` → `8000` 으로 프록시한다.  
따라서 `client`에서 `npm run dev` 로 UI 띄운 뒤, 같은 터미널이 아닌 **다른 터미널**에서 `npm run dev:api` 를 같이 켜 두면 `fetch('/api/...')` 로 호출 가능하다.

## DB 연결

Python에서는 **PyMySQL** (`requirements.txt` 의 `PyMySQL` 패키지)으로 MariaDB에 접속한다. Railway 등 Linux 빌드에서 네이티브 `mariadb` 패키지 빌드(Connector/C)를 피하기 위해 선택했다.

## 환경 변수

루트 `.env` — `docs` 의 DB 예시와 동일 (`DB_*`). 비밀번호는 저장소에 올리지 않는다.

## Railway 배포 시

Uvicorn으로 `backend.main:app` 을 실행하면 된다. 포트는 플랫폼이 주는 `PORT` 환경 변수에 맞추면 된다.

**Railway 전체 절차·DB 사설 엔드포인트·환경 변수 표는 `docs/railway-deploy.md` 를 참조한다.**

## 인증 로드맵

- 모바일 JWT(access/refresh)는 현재 적용되어 있다.
- 관리자 JWT는 UI를 먼저 두고 마지막 단계에서 적용한다.
- 상세 절차는 `docs/admin-jwt-implementation-plan.md` 를 따른다.
- 연차촉진(모바일 푸시 + 확인/서명) 계획은 `docs/leave-promotion-implementation-plan.md` 를 따른다.
