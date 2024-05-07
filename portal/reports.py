from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db, get_current_period

bp = Blueprint('reports', __name__)


@bp.route("/reports")
def index():
    return render_template('reports/index.html')


@bp.route("/reports/<string:category>/new", methods=('GET', 'POST',))
@login_required
def new(category):
    current_period = get_current_period()
    db = get_db()
    valid_periods = db.execute(
        'SELECT accounting_period'
        ' FROM accounting_period'
        ' WHERE id <= ?',
        (current_period,)
    )
    return render_template('reports/new.html', valid_periods=valid_periods, category=category)


