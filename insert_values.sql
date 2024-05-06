-- INSERT INTO job_details (user_id, period_id, name_id, status_id)
-- VALUES
--     (1, 1, 1, 1),
--     (1, 5, 2, 3),
--     (1, 6, 2, 5),
--     (1, 6, 2, 2),
--     (1, 6, 9, 4),
--     (1, 2, 6, 2);

-- INSERT INTO job_status (status)
-- VALUES
--     ('Cancelled');

CREATE TABLE manual_adjustment_upload (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  period_id INTEGER NOT NULL,
  status_id INTEGER NOT NULL,
  upload_path TEXT NOT NULL,
  attachment_path TEXT NOT NULL,
  is_gross INTEGER NOT NULL CHECK (is_gross IN (0, 1)),
  post_to_ledger INTEGER NOT NULL CHECK (post_to_ledger IN (0, 1)),
  adj_type TEXT NOT NULL CHECK (adj_type IN ('REV', 'PERM', 'QTR')),
  notify_email TEXT,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (period_id) REFERENCES accounting_period (id),
  FOREIGN KEY (status_id) REFERENCES job_status (id)
);