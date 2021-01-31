import mysql.connector
import click
from flask import current_app, g
from flask.cli import with_appcontext
from .sql import constl

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'],
            password=current_app.config['DATABASE_PASSWORD'],
            user=current_app.config['DATABASE_USER'],
            database=current_app.config['DATABASE']
        )
        g.cursor = g.db.cursor(dictionary=True)
    return g.db, g.cursor

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db, c = get_db()
    for sql_inst in constl:
        c.execute(sql_inst)
    db.commit()

@click.command('init_db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB setted. Data deleted')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
