DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS job_type;
DROP TABLE IF EXISTS job_name;
DROP TABLE IF EXISTS job_status;
DROP TABLE IF EXISTS accounting_period;
DROP TABLE IF EXISTS job_details;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

    -- INSERT INTO user (username, password)
    -- VALUES ('admin', 'admin');


CREATE TABLE job_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT UNIQUE NOT NULL
);

    INSERT INTO job_type (type)
    VALUES 
        ('General'),
        ('Gross Close'),
        ('Gross Post-Close');


CREATE TABLE job_name (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  type_id INTEGER NOT NULL,
  FOREIGN KEY (type_id) REFERENCES job_type (id)
);

    INSERT INTO job_name (name, type_id)
    VALUES
        ('Change Accounting Period', '1'),
        ('Upload Manual Adjustment', '1'),
        ('Run Reports', '1'),
        ('Data Quality Checks', '1'),
        ('Gross Postbox', '2'),
        ('Gross Balance Sheet Reconciliations', '2'),
        ('Gross Income Statement Reconciliations', '2'),
        ('Run Gross Reports', '2'),
        ('Gross CECL Adjustment', '3');


CREATE TABLE job_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  status TEXT UNIQUE NOT NULL
);
    INSERT INTO job_status (status)
    VALUES
        ('Pending'),
        ('In Progress'),
        ('Success'),
        ('Failure'),
        ('Unknown');


CREATE TABLE accounting_period (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  accounting_period TEXT UNIQUE NOT NULL,
  is_open INTEGER DEFAULT 0 CHECK (is_open IN (0, 1)),
  is_current INTEGER DEFAULT 0 CHECK (is_current IN (0, 1))
);

CREATE TRIGGER enforce_single_is_current
BEFORE INSERT ON accounting_period
WHEN NEW.is_current = 1
BEGIN
    SELECT CASE
        WHEN EXISTS (SELECT 1 FROM accounting_period WHERE is_current = 1 AND id != NEW.id)
        THEN RAISE (ABORT, 'Only one row can be active.')
    END;
END;

    INSERT INTO accounting_period (accounting_period, is_open, is_current)
    VALUES
      ('202312', 1, 0),
      ('202401', 1, 0),
      ('202402', 1, 0),
      ('202403', 1, 0),
      ('202404', 1, 0),
      ('202405', 1, 1),
      ('202406', 0, 0),
      ('202407', 0, 0),
      ('202408', 0, 0),
      ('202409', 0, 0),
      ('202410', 0, 0),
      ('202411', 0, 0),
      ('202412', 0, 0);

CREATE TABLE job_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  period_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  name_id INTEGER NOT NULL,
  status_id INTEGER NOT NULL,
  FOREIGN KEY (period_id) REFERENCES accounting_period (id),
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (name_id) REFERENCES job_name (id),
  FOREIGN KEY (status_id) REFERENCES job_status (id)
);