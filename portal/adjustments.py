from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db, get_open_periods, get_period_id_from_period

bp = Blueprint('adjustments', __name__)


@bp.route("/adjustments")
def index():
    db = get_db()
    adj_details = db.execute(   
        'SELECT adj.id, ap.accounting_period, adj.is_gross, adj.adj_type, adj.post_to_ledger, adj.upload_path, js.status, u.username, adj.created, adj.user_id'
        ' FROM manual_adjustment_upload adj'
        ' INNER JOIN accounting_period ap ON adj.period_id = ap.id'
        ' INNER JOIN user u ON adj.user_id = u.id'
        ' INNER JOIN job_status js ON adj.status_id = js.id'
    ).fetchall()
    return render_template('adjustments/index.html', adj_details = adj_details)

@bp.route("/adjustments/upload", methods=('GET', 'POST'))
@login_required
def upload():
    open_periods = get_open_periods()
    
    if request.method == 'POST':
        period = str(request.form['period'])
        is_gross = int(request.form['is-gross'])
        adj_type = request.form['adj-type']
        post_to_ledger = int(request.form['post-to-ledger'])
        upload_path = request.form['upload-path']
        attachment_path = request.form['attachment-path']
        notify_email = request.form['notify-email'].replace('\n', ';').replace('\r','')

        if attachment_path is None or attachment_path == "":
            attachment_path = upload_path

        error = None

        if len(period) != 6:
            error = "Make a selection for Accounting Period."
        elif is_gross is None:
            error = "Make a selection for Gross or Ceded."
        elif adj_type is None:
            error = "Make a selection for Adjustment Type."
        elif post_to_ledger is None:
            error = "Make a selection for Post Adjustment to Ledger."
        elif len(upload_path) < 5:
            error = "Enter a valid .xlsx filepath for the Adjustment file."
        elif upload_path.lower()[-5:] not in ".xlsx":
            error = "Adjustment file must be a .xlsx file."
        elif upload_path.upper().startswith("C"):
            error = f"Adjustment file must be saved on a shared network.\nIt looks like the file {upload_path} is saved to your C drive."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            period_id = get_period_id_from_period(period)
            db.execute(
                'INSERT INTO manual_adjustment_upload (user_id, period_id, is_gross, adj_type, post_to_ledger, upload_path, attachment_path, notify_email, status_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], period_id, is_gross, adj_type, post_to_ledger, upload_path, attachment_path, notify_email, 1,)
            )
            db.commit()
            flash(f"Upload of {upload_path} added to queue. (ID={get_last_upload_id()})")
            return redirect(url_for('adjustments.index'))
            
    return render_template('adjustments/upload.html', open_periods=open_periods)

@bp.route("/adjustments/<int:id>/view", methods=('GET', 'POST'))
@login_required
def view(id):
    adj_details = get_upload_details(id, check_author=False)
    return render_template('adjustments/view.html', adj_details=adj_details)


@bp.route("/adjustments/<int:id>/cancel", methods=('POST',))
@login_required
def cancel(id):
    get_upload_details(id, check_author=True)
    db = get_db()
    db.execute(
        'UPDATE manual_adjustment_upload'
        ' SET status_id = 6'
        ' WHERE id = ?',
        (id,)
    )
    db.commit()
    flash(f"Task cancelled (ID={id}).")
    return redirect(url_for('adjustments.index'))

@bp.route("/adjustments/<int:id>/repeat", methods=('POST',))
@login_required
def repeat(id):
    adj_details = get_upload_details(id, check_author=False)
    flash("Not implemented yet...")
    return render_template('adjustments/view.html', adj_details=adj_details)

def get_last_upload_id():
    db = get_db()
    return db.execute('SELECT id FROM manual_adjustment_upload ORDER BY id DESC').fetchone()[0]

def get_upload_details(id, check_author=True):
    db = get_db()
    adj_details = db.execute(
        'SELECT adj.id, ap.accounting_period, adj.is_gross, adj.adj_type, adj.post_to_ledger, adj.upload_path, js.status, u.username, adj.created, adj.user_id'
        ' FROM manual_adjustment_upload adj'
        ' INNER JOIN accounting_period ap ON adj.period_id = ap.id'
        ' INNER JOIN user u ON adj.user_id = u.id'
        ' INNER JOIN job_status js ON adj.status_id = js.id'
        ' WHERE adj.id = ?',
        (id,)
    ).fetchone()

    if adj_details is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and adj_details['user_id'] != g.user['id']:
        abort(403)

    return adj_details