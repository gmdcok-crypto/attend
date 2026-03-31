-- 개인별 휴가 기록 + 연간 한도(선택, 남은일수 계산용)
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS employee_leave_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_id BIGINT UNSIGNED NOT NULL,
  leave_code_id BIGINT UNSIGNED NOT NULL,
  start_date DATE NOT NULL COMMENT '휴가 시작',
  end_date DATE NOT NULL COMMENT '휴가 종료',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  KEY idx_elr_emp_leave (employee_id, leave_code_id),
  KEY idx_elr_range (start_date, end_date),
  CONSTRAINT fk_elr_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_elr_leave_code FOREIGN KEY (leave_code_id) REFERENCES leave_codes (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사원 휴가 사용 기록';

CREATE TABLE IF NOT EXISTS employee_leave_quotas (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_id BIGINT UNSIGNED NOT NULL,
  leave_code_id BIGINT UNSIGNED NOT NULL,
  year_year SMALLINT NOT NULL COMMENT '적용 연도',
  quota_days DECIMAL(7, 1) NOT NULL DEFAULT 0 COMMENT '부여 일수',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_elq_emp_leave_year (employee_id, leave_code_id, year_year),
  KEY idx_elq_emp (employee_id),
  CONSTRAINT fk_elq_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_elq_leave FOREIGN KEY (leave_code_id) REFERENCES leave_codes (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사원·휴가코드별 연간 한도';

SET FOREIGN_KEY_CHECKS = 1;
