-- 근태 DB 초기 스키마 (MariaDB / MySQL 8+)
-- DB: attend · 문자셋 utf8mb4 · 시각 의미는 KST (docs/korea-time-and-infrastructure.md)
-- 적용 예: mariadb -u attend -p attend < sql/001_init.sql
--          (없으면 mysql ... 동일)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 부서
CREATE TABLE IF NOT EXISTS departments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(32) NOT NULL COMMENT '부서코드',
  name VARCHAR(128) NOT NULL COMMENT '부서명',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_departments_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부서';

-- 사원
CREATE TABLE IF NOT EXISTS employees (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_no VARCHAR(32) NOT NULL COMMENT '사번',
  name VARCHAR(64) NOT NULL COMMENT '성명',
  department_id BIGINT UNSIGNED NULL COMMENT '부서 FK',
  hire_date DATE NULL COMMENT '입사일',
  status VARCHAR(16) NOT NULL DEFAULT '재직' COMMENT '재직, 휴직 등',
  password_hash VARCHAR(255) NULL COMMENT 'bcrypt 해시',
  auth_status CHAR(1) NOT NULL DEFAULT 'X' COMMENT 'O=인증완료, X=미완료',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_employees_no (employee_no),
  KEY idx_employees_department (department_id),
  CONSTRAINT fk_employees_department FOREIGN KEY (department_id) REFERENCES departments (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사원';

-- 휴가 코드
CREATE TABLE IF NOT EXISTS leave_codes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(32) NOT NULL COMMENT '휴가코드',
  name VARCHAR(128) NOT NULL COMMENT '명칭',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_leave_codes_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='휴가 코드';

-- 출퇴근 원시 이벤트 (태블릿 QR·수동 등)
CREATE TABLE IF NOT EXISTS attendance_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_id BIGINT UNSIGNED NOT NULL,
  event_type ENUM('IN', 'OUT') NOT NULL COMMENT 'IN=출근, OUT=퇴근',
  occurred_at DATETIME(3) NOT NULL COMMENT '발생 시각 (KST 의미)',
  source VARCHAR(32) NULL DEFAULT 'QR' COMMENT 'QR, MANUAL 등',
  device_info VARCHAR(255) NULL COMMENT '단말/UA 요약',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  KEY idx_attendance_emp_time (employee_id, occurred_at),
  CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='출퇴근 원시 로그';

SET FOREIGN_KEY_CHECKS = 1;
