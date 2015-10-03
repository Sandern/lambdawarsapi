from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.default_settings')
app.config.from_pyfile('application.cfg', silent=True)

@app.route('/')
def lambda_wars_api():
    return 'Lambda Wars API'

from . import matches

from .database import db_session, init_db

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Temporary always call init_db, since it's just a temp sqlite db
init_db()