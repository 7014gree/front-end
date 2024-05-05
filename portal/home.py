from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db

bp = Blueprint('home', __name__)


@bp.route("/")
def index():
    db = get_db()
    jobs = db.execute(
        'SELECT jd.id, ap.accounting_period, jd.user_id, u.username, jd.created, jt.type, jn.name, js.status FROM job_details jd'
        ' INNER JOIN user u ON u.id = jd.user_id'
        ' INNER JOIN accounting_period ap ON ap.id = jd.period_id'
        ' INNER JOIN job_name jn ON jn.id = jd.name_id'
        ' INNER JOIN job_type jt ON jt.id = jn.type_id'
        ' INNER JOIN job_status js ON js.id = jd.status_id'
        ' ORDER BY jd.created ASC'
    ).fetchall()
    return render_template('home/index.html', jobs=jobs)