# 태블릿 · 출근 인증 QR

## 열기

- 개발(PC 브라우저): `http://localhost:5173/tablet.html`
- **같은 Wi‑Fi의 태블릿**: PC의 사설 IP로 `http://192.168.x.x:5173/tablet.html` (Vite는 `vite.config.ts`의 `server.host: true`로 LAN 접속 허용)
- `npm run dev` 변경 후에는 **개발 서버를 한 번 재시작**해야 설정이 반영된다.
- 화면이 안 뜨면 Windows 방화벽에서 **Node.js(또는 포트 5173)** 인바운드 허용 여부를 확인한다.
- 빌드 후: `dist/tablet.html`을 동일 경로로 서빙

## 동작 (목업)

- **동적 QR**: 약 30초마다 페이로드(JSON)를 바꾸고 QR을 다시 그립니다.
- **시각 표시**: `Asia/Seoul`(KST) 기준 현재 시각을 표시합니다. (`docs/korea-time-and-infrastructure.md`와 동일 원칙)
- 실제 서비스에서는 Railway API에서 발급한 토큰·만료 시각으로 페이로드를 바꾸면 됩니다.
