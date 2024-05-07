from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db, get_open_periods, get_period_id_from_period, change_job_status

bp = Blueprint('jobs', __name__)


@bp.route("/jobs")
def index():
    db = get_db()
    jobs = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE js.status IN (?, ?)'
        ' ORDER BY jd.id ASC',
        ("Pending", "In Progress",)
    ).fetchall()
    return render_template('jobs/index.html', jobs=jobs, all=False)

@bp.route("/jobs/all")
def all_jobs():
    db = get_db()
    jobs = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' ORDER BY jd.id ASC'
    ).fetchall()
    return render_template('jobs/index.html', jobs=jobs, all=True)


@bp.route("/jobs/my_jobs")
def my_jobs():
    db = get_db()
    my_jobs_in_progress = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE u.id = ?'
        ' AND js.status = ?'
        ' ORDER BY jd.created ASC',
        (g.user['id'], "In Progress",)
    ).fetchall()
    my_jobs_pending = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE u.id = ?'
        ' AND js.status = ?'
        ' ORDER BY jd.created ASC',
        (g.user['id'], "Pending",)
    ).fetchall()
    my_jobs_completed = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE u.id = ?'
        ' AND js.status IN (?, ?)'
        ' ORDER BY jd.created ASC',
        (g.user['id'], "Success", "Failure",)
    ).fetchall()
    my_jobs_unknown = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE u.id = ?'
        ' AND js.status = ?'
        ' ORDER BY jd.created ASC',
        (g.user['id'], "Unknown",)
    ).fetchall()
    return render_template('jobs/my_jobs.html',
                           my_jobs_in_progress=my_jobs_in_progress,
                           my_jobs_pending=my_jobs_pending,
                           my_jobs_completed=my_jobs_completed,
                           my_jobs_unknown=my_jobs_unknown)


@bp.route("/jobs/<string:type>/new", methods=('GET', 'POST'))
@login_required
def new(type):
    db = get_db()
    open_periods = get_open_periods()
    job_names = db.execute(
        'SELECT jn.id, jn.name, jt.type'
        ' FROM job_name jn'
        ' INNER JOIN job_type jt on jt.id = jn.type_id'
        ' WHERE jt.type = ?',
        (type,)
    ).fetchall()

    if request.method == 'POST':
        period = request.form['period']
        name = request.form['name']
        error = None

        if not period:
            error = 'Period selection is required.'
        elif not name:
            error = 'Task selection is required.'
        print(request.form, period, name)

        if error is not None:
            flash(error)
        else:
            period_id = get_period_id_from_period(period)
            name_id = db.execute(
                'SELECT id FROM job_name'
                ' WHERE name = ?',
                (name,)
            ).fetchone()[0]      

            job_added, existing_job_id = add_job(period_id=period_id, name_id=name_id, user_id=g.user['id'])
            if job_added:
                flash(f"Task added (ID={get_last_task_id()})")
                return redirect(url_for('jobs.index'))
            flash(f"Unable to create task as an equivalent task (ID={existing_job_id}) is either 'Pending' or 'In Progress'.")

    return render_template('jobs/new.html', open_periods=open_periods, job_names=job_names, type=type)



def get_job(id, check_author=True):
    job_details = get_db().execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status, jd.period_id, jd.name_id FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' WHERE jd.id = ?',
        (id,)
    ).fetchone()

    if job_details is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and job_details['user_id'] != g.user['id']:
        abort(403)

    return job_details

@bp.route('/jobs/<int:id>/view')
def view(id):
    job = get_job(id, check_author=False)
    return render_template('jobs/view.html', job=job)

@bp.route('/jobs/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_job(id)
    db = get_db()
    # db.execute(
    #     'DELETE FROM job_details'
    #     ' WHERE id = ?',
    #     (id,)
    # )
    # db.commit()
    print("Deleted!!")
    return redirect(url_for('jobs.index'))

@bp.route('/jobs/<int:id>/cancel', methods=('POST',))
@login_required
def cancel(id):
    get_job(id)
    change_job_status(job_id=id, status_id=6)
    flash(f"Task cancelled (ID={id}).")
    return redirect(url_for('jobs.index'))

@bp.route('/jobs/<int:id>/repeat', methods=('POST',))
@login_required
def repeat(id):
    job = get_job(id, check_author=False)
    job_added, existing_job_id = add_job(period_id=job['period_id'], name_id=job['name_id'], user_id=g.user['id'])
    if not job_added:
        flash(f"Unable to repeat task (ID={job['id']}) as an equivalent task (ID={existing_job_id}) is either 'Pending' or 'In Progress'.")
    else:
        flash(f"Task (ID={id}) repeated (ID={get_last_task_id()}).")
    return redirect(url_for('jobs.index'))

def get_last_task_id():
    db = get_db()
    return db.execute('SELECT id FROM job_details ORDER BY id DESC').fetchone()[0]

def add_job(period_id, name_id, user_id):
    db = get_db()
    current_job = db.execute(
        'SELECT * FROM job_details'
        ' WHERE period_id = ?'
        ' AND name_id = ?'
        ' AND status_id IN (1, 2)',
        (period_id, name_id,)
    ).fetchone()
    if not current_job:
        db.execute(
            'INSERT INTO job_details (period_id, name_id, user_id, status_id)'
            ' VALUES (?, ?, ?, ?)',
            (period_id, name_id, user_id, 1,)
        )
        db.commit()
        return (True, 0,)
    return (False, current_job['id'],)