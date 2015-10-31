from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.default_settings')
app.config.from_pyfile('application.cfg', silent=True)

@app.route('/')
def lambda_wars_api():
    return 'Lambda Wars API'

from . import matches
from . import database
