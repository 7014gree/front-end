DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS job_type;
DROP TABLE IF EXISTS job_name;
DROP TABLE IF EXISTS job_status;
DROP TABLE IF EXISTS job_details;


CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

    INSERT INTO users (username, password)
    VALUES ('admin', 'admin');


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


CREATE TABLE job_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_id INTEGER NOT NULL,
  name_id INTEGER NOT NULL,
  status_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (name_id) REFERENCES job_name (id),
  FOREIGN KEY (status_id) REFERENCES job_status (id)
);