# 백엔드 — FastAPI

Node(Express) 대신 **FastAPI + Uvicorn**으로 API를 통일했다.

## 준비

```bash
python -m pip install -r backend/requirements.txt
```

(권장) 가상환경: `python -m venv .venv` 후 활성화하고 위 `pip install` 실행.

## 실행

프로젝트 루트(`d:\attend`)에서:

```bash
npm run dev:api
```

- API: `http://127.0.0.1:8000`
- 연결 확인: `GET http://127.0.0.1:8000/api/db/ping`
- 문서: `http://127.0.0.1:8000/docs` (Swagger UI)

프론트(Vite)는 `vite.config.ts`에서 `/api` → `8000` 으로 프록시한다.  
따라서 `npm run dev` 로 UI 띄운 뒤, 같은 터미널이 아닌 **다른 터미널**에서 `npm run dev:api` 를 같이 켜 두면 `fetch('/api/...')` 로 호출 가능하다.

## DB 연결

Python에서는 **MariaDB 공식 Connector/Python** (`requirements.txt` 의 `mariadb` 패키지, `import mariadb`)을 사용한다. PyMySQL이 아니다.

## 환경 변수

루트 `.env` — `docs` 의 DB 예시와 동일 (`DB_*`). 비밀번호는 저장소에 올리지 않는다.

## Railway 배포 시

Uvicorn으로 `backend.main:app` 을 실행하면 된다. 포트는 플랫폼이 주는 `PORT` 환경 변수에 맞추면 된다.

**Railway 전체 절차·DB 사설 엔드포인트·환경 변수 표는 `docs/railway-deploy.md` 를 참조한다.**
