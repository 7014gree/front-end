from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db, get_period_id_from_period, get_current_period, get_period_from_id

bp = Blueprint('settings', __name__)

@bp.route("/settings")
@login_required
def index():
    return render_template('settings/index.html')

@bp.route("/settings/periods", methods=('GET', 'POST',))
@login_required
def periods():
    db = get_db()
    current_period = db.execute(
        'SELECT id FROM accounting_period'
        ' WHERE is_current = 1'
    ).fetchone()[0]
    all_periods = db.execute(
        'SELECT * FROM accounting_period'
        ' ORDER BY accounting_period ASC'
    ).fetchall()
    
    return render_template('settings/periods.html', all_periods=all_periods, current_period=current_period)

@bp.route("/settings/periods/<int:id>/open", methods=('POST',))
@login_required
def open_period(id):
    change_period(id=id, open=True)
    flash(f"Set {get_period_from_id(id)} to 'Open'.")
    return redirect(url_for('settings.periods'))

@bp.route("/settings/periods/<int:id>/close", methods=('POST',))
@login_required
def close_period(id):
    change_period(id=id, open=False)
    flash(f"Set {get_period_from_id(id)} to 'Closed'.")
    return redirect(url_for('settings.periods'))

@bp.route("/settings/periods/<int:id>/current", methods=('GET', 'POST',))
@login_required
def set_current_period(id):
    db = get_db()
    db.execute(
        'UPDATE accounting_period'
        ' SET is_current = 0'
        ' WHERE is_current = 1'
    )
    db.commit()
    db.execute(
        'UPDATE accounting_period'
        ' SET is_current = 1'
        ' WHERE id = ?',
        (id,)
    )
    db.commit()
    change_period(id=id, open=True)
    flash(f"Set {get_period_from_id(id)} to 'Current'.")
    return redirect(url_for('settings.periods'))

def change_period(id, open):
    db = get_db()
    db.execute(
        'UPDATE accounting_period'
        ' SET is_open = ?'
        ' WHERE id = ?',
        (int(open), id,)
    )
    db.commit()