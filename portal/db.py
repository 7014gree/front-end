import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialised the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_open_periods():
    db = get_db()
    open_periods = db.execute(
        'SELECT id, accounting_period'
        ' FROM accounting_period'
        ' WHERE is_open = 1'
    ).fetchall()
    return open_periods

def get_period_id_from_period(period: str) -> int | None:
    db = get_db()
    period_id = db.execute(
                'SELECT id FROM accounting_period'
                ' WHERE accounting_period = ?',
                (period,)
            ).fetchone()[0]
    return period_id

def get_current_period():
    db = get_db()
    current_period = db.execute(
        'SELECT id FROM accounting_period'
        ' WHERE is_current = 1'
    ).fetchone()[0]
    return current_period

def get_period_from_id(id):
    db = get_db()
    period_str = db.execute(
        'SELECT accounting_period'
        ' FROM accounting_period'
        ' WHERE id = ?',
        (id,)
    ).fetchone()[0]
    return period_str

def change_job_status(job_id, status_id):
    db = get_db()
    db.execute(
        'UPDATE job_details'
        ' SET status_id = ?'
        ' WHERE id = ?',
        (status_id, job_id,)
    )
    db.commit()