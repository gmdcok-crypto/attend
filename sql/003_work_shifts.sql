-- 근무시간(근태) 유형: 출·퇴근 기준 시각
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS work_shift_types (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL COMMENT '근태명',
  clock_in TIME NOT NULL COMMENT '출근',
  clock_out TIME NOT NULL COMMENT '퇴근',
  sort_order INT NOT NULL DEFAULT 0 COMMENT '표시 순서',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  KEY idx_work_shift_sort (sort_order, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='근무시간 유형';
