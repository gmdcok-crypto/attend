# 연차촉진(모바일 푸시 + 확인/서명) 구현 계획

## 목표

- 연차촉진 대상자에게 모바일 푸시를 발송한다.
- 직원이 앱에서 안내문을 확인하고 전자서명(확인)을 남긴다.
- 발송/열람/서명 이력을 감사용으로 추적 가능하게 유지한다.

## 적용 원칙

1. 민감정보는 푸시 payload에 넣지 않는다.
   - 푸시에는 알림 제목/요약 + 딥링크 키만 포함한다.
   - 상세 내용은 앱이 API로 재조회한다.
2. 서명 증적은 append-only 성격으로 보관한다.
   - 누가/언제/어떤 문서 버전에 서명했는지 재현 가능해야 한다.
3. 모바일 인증(JWT) 체계를 재사용한다.
   - 기존 access/refresh 검증 흐름 위에서 연차촉진 API를 보호한다.

## 최소 기능 범위(MVP)

1. 대상자 추출
   - 기준일/잔여 연차/사용 이력 기준으로 촉진 대상자 계산
2. 발송
   - 관리자 화면에서 즉시 발송 + 예약 발송
   - 중복 발송 방지(같은 캠페인/같은 직원)
3. 앱 확인
   - 푸시 클릭 시 연차촉진 화면 진입
   - 안내문 열람 시각 기록
4. 전자서명(확인)
   - 직원 확인 버튼 + PIN 2차 확인(서버 검증 방식)
   - 서명 시점 문서 해시 저장
5. 이력 조회
   - 관리자에서 발송 성공/실패/열람/서명 현황 확인

## 서버/DB 초안

### 테이블

- `mobile_push_tokens`
  - `employee_id`, `platform`, `device_token`, `enabled`, `updated_at`
- `leave_promotion_campaigns`
  - `id`, `title`, `doc_version`, `message`, `scheduled_at`, `created_by`, `created_at`
- `leave_promotion_targets`
  - `campaign_id`, `employee_id`, `send_status`, `sent_at`, `read_at`, `signed_at`
- `leave_promotion_signatures`
  - `campaign_id`, `employee_id`, `doc_hash`, `signed_at`, `ip`, `user_agent`, `device_id`

### API(초안)

- 관리자
  - `POST /api/leave-promotion/campaigns`
  - `POST /api/leave-promotion/campaigns/{id}/send`
  - `GET /api/leave-promotion/campaigns/{id}/status`
- 모바일
  - `GET /api/mobile/leave-promotion/current`
  - `POST /api/mobile/leave-promotion/{id}/read`
  - `POST /api/mobile/leave-promotion/{id}/sign`

## 발송/서명 흐름

1. 관리자에서 캠페인 생성
2. 대상자 계산 후 푸시 발송(FCM/APNs)
3. 직원 앱 진입 후 상세문서 조회
4. 읽음 기록 저장
5. PIN 재입력 후 서버 검증 성공 시 서명 확정
6. 서명 확정 시 `doc_hash + 메타데이터` 저장
7. 관리자 화면에서 실시간/주기 갱신으로 현황 확인

## PIN 2차인증(서버 검증) 기본안

연차촉진 전자서명의 기본 2차인증은 "PIN + 서버 검증"으로 한다.

### 원칙

- PIN 원문은 서버/클라이언트 어디에도 저장하지 않는다.
- 서버에는 PIN 해시(예: `bcrypt`)만 저장한다.
- 서명 시도마다 서버에서 PIN을 직접 검증한다.
- 실패 횟수 제한 및 잠금 정책을 적용한다.

### API(초안)

- `POST /api/mobile/pin/setup` (최초 설정/재설정)
- `POST /api/mobile/pin/verify` (서명 직전 검증)
- `POST /api/mobile/leave-promotion/{id}/sign` (verify 성공 직후 호출)

### 운영 정책(권장)

- PIN 6자리 숫자
- 5회 연속 실패 시 일정 시간 잠금
- PIN 변경 시 기존 서명 세션 무효화
- 검증/실패/잠금 이벤트 감사로그 저장

## 보안/운영 체크리스트

- 토큰/시크릿
  - `FCM_SERVER_KEY` 또는 서비스 계정
  - iOS 사용 시 APNs 키/인증서
- 보안
  - 푸시 payload 민감정보 금지
  - 서명 원문/해시 검증 API 제공
  - 재서명/철회 이력 분리 저장
- 운영
  - 실패 재시도 큐
  - 발송량 제한(레이트 리밋)
  - 감사 리포트 다운로드(CSV/PDF)

## 구현 단계 제안

1. DB 스키마 + 토큰 수집 API
2. 관리자 연차촉진 화면(대상 조회/발송 버튼)
3. 푸시 발송 워커/잡
4. 모바일 열람/서명 화면 및 API
5. 이력 대시보드 + 감사 리포트

## 모바일 연차사용 계획 기능(확장)

연차촉진과 별개로, 모바일에서 연차사용 "계획"을 먼저 등록하는 흐름을 추가할 수 있다.

### 목표

- 직원이 모바일에서 연차 사용 예정일을 미리 등록/수정/취소한다.
- 관리자는 계획 현황을 보고 인력 운영을 사전에 조정한다.
- 추후 승인 워크플로우(결재선)로 확장 가능한 구조를 유지한다.

### 최소 기능 범위(MVP)

1. 계획 등록
   - 단일일/기간 선택, 사유(선택), 반차 구분(선택)
2. 계획 수정/취소
   - 계획 상태가 확정 전일 때만 변경 허용
3. 유효성 검사
   - 잔여 연차 부족, 기간 중복, 공휴일/휴무일 충돌 검사
4. 관리자 조회
   - 부서/기간/상태 필터로 계획 목록 조회
5. 이력 저장
   - 생성/수정/취소 시각 및 변경자 기록

### DB/API 초안

- 테이블
  - `leave_plan_requests`
    - `id`, `employee_id`, `date_from`, `date_to`, `leave_unit`, `reason`, `status`, `created_at`, `updated_at`
  - `leave_plan_request_logs`
    - `request_id`, `action`, `before_json`, `after_json`, `actor_id`, `created_at`
- API
  - 모바일
    - `POST /api/mobile/leave-plans`
    - `PUT /api/mobile/leave-plans/{id}`
    - `DELETE /api/mobile/leave-plans/{id}`
    - `GET /api/mobile/leave-plans/me`
  - 관리자
    - `GET /api/admin/leave-plans`
    - `PATCH /api/admin/leave-plans/{id}/status` (추후 승인단계용)

### 구현 순서 제안

1. 모바일 계획 등록/목록 API
2. 모바일 화면(캘린더 + 계획 리스트)
3. 관리자 조회 화면(연차촉진 메뉴와 연동 가능)
4. 충돌 검사 고도화(근무표/공휴일/대체휴무)
5. 승인/반려 프로세스 확장

