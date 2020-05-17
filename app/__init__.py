from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.default_settings')
app.config.from_pyfile('application.cfg', silent=True)
CORS(app)

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['LOG_PATH'])
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

@app.route('/')
def lambda_wars_api():
    return 'Lambda Wars API'

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(success=False), 500

from . import matches
from . import database
