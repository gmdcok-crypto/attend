-- 개인별 휴가 기록 (잔여는 입사일·기록으로 산정; employee_leave_quotas 테이블은 사용하지 않음)
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

SET FOREIGN_KEY_CHECKS = 1;
