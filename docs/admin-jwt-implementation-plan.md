# 관리자 인증(JWT) 구현 계획

## 현재 원칙

- 관리자 설정 메뉴는 **UI만 먼저 제공**한다.
- 관리자 인증 백엔드(로그인, 토큰 검증, 비밀번호 변경)는 **프로젝트 마지막 단계**에서 구현한다.
- 중간 단계에서는 관리자 설정 저장 버튼이 실제 DB를 변경하지 않도록 유지한다.

## 모바일 인증 로직 재사용 원칙

관리자 인증은 모바일과 동일한 패턴을 따른다.

1. **Access Token + Refresh Token 분리**
   - access: `60분`
   - refresh: `14일`
2. **401 발생 시 백그라운드 재발급**
   - 클라이언트가 `/api/admin/auth/refresh` 호출
   - 성공 시 원래 요청 1회 자동 재시도
3. **Refresh Rotation**
   - refresh 1회 사용 시 기존 토큰 폐기 + 새 refresh 발급
4. **DB에는 refresh 원문이 아닌 해시 저장**
   - `SHA-256(token)` 저장

## 최종 구현 순서(마지막 단계)

1. DB
   - `admin_users` 테이블(아이디, 비밀번호 해시, 상태, 생성/수정시각)
   - `admin_refresh_tokens` 테이블(토큰 해시, 만료, 폐기시각, 관리자 FK)
2. 백엔드
   - `/api/admin/auth/login`
   - `/api/admin/auth/refresh`
   - `/api/admin/auth/me`
   - `/api/admin/auth/change-password`
   - admin 전용 dependency (`role=admin` / `typ=admin_access` 검증)
3. 프론트(admin)
   - `admin_session` 저장소 분리
   - API 유틸에 401 자동 refresh 재시도 적용
   - `/admin.html` 진입 시 로그인 선확인
4. 보안 마무리
   - 로그인 실패 횟수 제한(브루트포스 완화)
   - 로그아웃 시 refresh 폐기
   - 비밀번호 변경 시 기존 refresh 전부 폐기

## 환경 변수(관리자 인증용)

- `ADMIN_JWT_SECRET` (관리자 토큰 서명 키)
- `ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES` (기본 60)
- `ADMIN_REFRESH_TOKEN_EXPIRE_DAYS` (기본 14)

## 비고

- 모바일 인증은 이미 운영 중이며, 관리자 인증은 동일 패턴으로 맞춘다.
- UI 문구/버튼은 지금처럼 유지하고, 마지막 단계에서만 API 연결을 붙인다.
