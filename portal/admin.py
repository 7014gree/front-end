from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db, get_period_id_from_period

bp = Blueprint('admin', __name__)

@bp.route("/admin", methods=('GET', 'POST',))
@login_required
def index():
    if g.user['id'] != 1:
        flash("Only user admin can access the Admin Panel.")
        return redirect(url_for('home.index'))
    if request.method == 'POST':
        try:
            db = get_db()
            db.execute(
                request.form['sql-query']
            )
            db.commit()
        except Exception as e:
            flash(f"Error running SQL query. {e}")
        else:
            flash(f"Successfully executed SQL query.")
    return render_template('admin/index.html')
