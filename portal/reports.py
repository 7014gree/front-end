from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from portal.auth import login_required
from portal.db import get_db

bp = Blueprint('reports', __name__)


@bp.route("/reports")
def index():
    return render_template('reports/index.html')

