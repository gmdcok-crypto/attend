"""기존 DB에 누락된 컬럼 보강 (마이그레이션 미적용 시에도 API 동작)."""

from __future__ import annotations

from pymysql.connections import Connection


def ensure_employee_auth_columns(conn: Connection) -> bool:
    """
    employees.password_hash, employees.auth_status 가 없으면 ALTER 로 추가.
    Returns True if at least one ALTER was executed.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'employees'
        """
    )
    existing = {str(row[0]).lower() for row in (cur.fetchall() or [])}
    changed = False

    if "password_hash" not in existing:
        cur.execute(
            """
            ALTER TABLE employees
            ADD COLUMN password_hash VARCHAR(255) NULL COMMENT 'bcrypt 해시' AFTER status
            """
        )
        changed = True

    if "auth_status" not in existing:
        cur.execute(
            """
            ALTER TABLE employees
            ADD COLUMN auth_status CHAR(1) NOT NULL DEFAULT 'X' COMMENT 'O=인증완료, X=미완료' AFTER password_hash
            """
        )
        changed = True

    return changed


def ensure_employee_leave_tables(conn: Connection) -> bool:
    """employee_leave_records / employee_leave_quotas 없으면 생성."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT TABLE_NAME FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (
          'employee_leave_records', 'employee_leave_quotas'
        )
        """
    )
    existing = {str(row[0]).lower() for row in (cur.fetchall() or [])}
    changed = False
    if "employee_leave_records" not in existing:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employee_leave_records (
              id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
              employee_id BIGINT UNSIGNED NOT NULL,
              leave_code_id BIGINT UNSIGNED NOT NULL,
              start_date DATE NOT NULL COMMENT '휴가 시작',
              end_date DATE NOT NULL COMMENT '휴가 종료',
              created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
              updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
                ON UPDATE CURRENT_TIMESTAMP(3),
              PRIMARY KEY (id),
              KEY idx_elr_emp_leave (employee_id, leave_code_id),
              KEY idx_elr_range (start_date, end_date),
              CONSTRAINT fk_elr_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
              CONSTRAINT fk_elr_leave_code FOREIGN KEY (leave_code_id) REFERENCES leave_codes (id)
                ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        changed = True
    if "employee_leave_quotas" not in existing:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employee_leave_quotas (
              id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
              employee_id BIGINT UNSIGNED NOT NULL,
              leave_code_id BIGINT UNSIGNED NOT NULL,
              year_year SMALLINT NOT NULL COMMENT '적용 연도',
              quota_days DECIMAL(7, 1) NOT NULL DEFAULT 0 COMMENT '부여 일수',
              created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
              updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
                ON UPDATE CURRENT_TIMESTAMP(3),
              PRIMARY KEY (id),
              UNIQUE KEY uk_elq_emp_leave_year (employee_id, leave_code_id, year_year),
              KEY idx_elq_emp (employee_id),
              CONSTRAINT fk_elq_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
              CONSTRAINT fk_elq_leave FOREIGN KEY (leave_code_id) REFERENCES leave_codes (id)
                ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        changed = True
    return changed


def ensure_work_shift_types_table(conn: Connection) -> bool:
    """work_shift_types 없으면 생성."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT TABLE_NAME FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'work_shift_types'
        """
    )
    if cur.fetchone():
        return False
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS work_shift_types (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          name VARCHAR(128) NOT NULL COMMENT '근태명',
          clock_in TIME NOT NULL COMMENT '출근',
          clock_out TIME NOT NULL COMMENT '퇴근',
          sort_order INT NOT NULL DEFAULT 0 COMMENT '표시 순서',
          created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
          updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
            ON UPDATE CURRENT_TIMESTAMP(3),
          PRIMARY KEY (id),
          KEY idx_work_shift_sort (sort_order, id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    return True


def ensure_mobile_refresh_tokens_table(conn: Connection) -> bool:
    """mobile_refresh_tokens 없으면 생성."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT TABLE_NAME FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'mobile_refresh_tokens'
        """
    )
    if cur.fetchone():
        return False
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mobile_refresh_tokens (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          employee_id BIGINT UNSIGNED NOT NULL,
          token_hash CHAR(64) NOT NULL COMMENT 'SHA-256(refresh_token)',
          expires_at DATETIME(3) NOT NULL,
          revoked_at DATETIME(3) NULL,
          created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
          PRIMARY KEY (id),
          UNIQUE KEY uk_mrt_token_hash (token_hash),
          KEY idx_mrt_employee (employee_id),
          KEY idx_mrt_expires (expires_at),
          CONSTRAINT fk_mrt_employee FOREIGN KEY (employee_id) REFERENCES employees (id)
            ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    return True
