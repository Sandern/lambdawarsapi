from flask import request, jsonify
from . import app
import uuid
import os

if not os.path.exists(app.instance_path):
    os.mkdir(app.instance_path)

matches_folder = os.path.join(app.instance_path, app.config['MATCHES_FOLDER'])
if not os.path.exists(matches_folder):
    os.mkdir(matches_folder)


@app.route('/matches/upload', methods=['POST'])
def upload_file():
    path = os.path.join(matches_folder, uuid.uuid4().hex)
    f = request.files['match_data']
    f.save(path)

    return jsonify(success=True)
