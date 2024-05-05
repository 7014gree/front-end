-- SELECT *--jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status
-- FROM job_details jd
-- INNER JOIN user u ON u.id = jd.user_id
-- INNER JOIN accounting_period ap ON ap.id = jd.period_id
-- INNER JOIN job_name jn ON jn.id = jd.name_id
-- INNER JOIN job_type jt ON jt.id = jn.type_id
-- INNER JOIN job_status js ON js.id = jd.status_id
-- ORDER BY jd.created ASC

SELECT jd.id, ap.accounting_period, jd.user_id, jd.created
FROM job_details jd
INNER JOIN accounting_period ap ON ap.id = jd.period_id
INNER JOIN "user" u ON u.id = jd.user_id