from flask import request, jsonify
from . import app
import uuid
import os
import zipfile
import json
from datetime import datetime

from .util import build_steamid, authenticate_ticket
from .database import db_session
from .models import Match, PlayerMatchResult

if not os.path.exists(app.instance_path):
    os.mkdir(app.instance_path)

matches_folder = os.path.join(app.instance_path, app.config['MATCHES_FOLDER'])
if not os.path.exists(matches_folder):
    os.mkdir(matches_folder)


@app.route('/matches/record_start', methods=['POST'])
def record_match_start():
    match_data = request.get_json()

    # Create the match id
    match_uuid = uuid.uuid4().hex

    # Create the match entry
    m_entry = Match()
    m_entry.submitter_ip = request.remote_addr
    m_entry.start_date = datetime.strptime(match_data['start_date'], '%Y-%m-%d %H:%M:%S')
    m_entry.mode = match_data['mode']
    m_entry.map = match_data['map']
    m_entry.match_uuid = match_uuid

    db_session.add(m_entry)
    db_session.commit()

    # Link players to match
    for player, data in match_data['players'].items():
        # No steamid means the player is a cpu
        if 'steamid' not in data:
            continue

        steamid = build_steamid(data['steamid'])

        p_entry = PlayerMatchResult()
        p_entry.steamid = steamid.as_64()
        p_entry.match_id = m_entry.id
        p_entry.verified = False

        db_session.add(p_entry)

    db_session.commit()

    return jsonify(success=True, match_uuid=match_uuid)


@app.route('/matches/verify_player', methods=['POST'])
def verify_player():
    auth_ticket = request.form.get("auth_ticket")
    match_uuid = request.form.get("match_uuid")

    steamid = authenticate_ticket(auth_ticket)
    if not steamid:
        return jsonify(success=False)

    result = PlayerMatchResult.query.filter(PlayerMatchResult.steamid == steamid.as_64() and
                                            PlayerMatchResult.match_uuid == match_uuid).one()

    result.verified = True
    db_session.commit()

    return jsonify(success=True)


@app.route('/matches/upload', methods=['POST'])
def upload_file():
    """ Records a match result from a game server. """
    match_uuid = request.form.get("match_uuid")

    m_entry = Match.query.filter(Match.match_uuid == match_uuid).one()

    if m_entry.submitter_ip != request.remote_addr:
        return jsonify(success=False)

    f = request.files['match_data']

    # Read the file as json
    # Could be too large? Probably not, but maybe.
    z = zipfile.ZipFile(f.stream)
    match_data = json.loads(z.read('stats.json').decode("utf-8"))

    # Update match metadata
    m_entry.duration = match_data['duration']
    m_entry.match_uuid = match_uuid

    db_session.commit()

    # Save the match file
    path = os.path.join(matches_folder, match_uuid)

    f.stream.seek(0)
    f.save(path)

    return jsonify(success=True)


def _matches_to_list(result):
    matches = []
    for r in result:
        matches.append({
            'steamid': r.steamid,
            'match_uuid': r.match_uuid,
            'duration': r.duration,
            'start_date': r.start_date,
            'mode': r.mode,
            'map': r.map,
        })
    return matches


@app.route('/player/matches/list/<steamid>', methods=['GET', 'POST'])
def list_matches_for_steamid(steamid):
    """ Lists the match history for a player. """
    steamid = build_steamid(steamid)

    result = Match.query.join(PlayerMatchResult, Match.id == PlayerMatchResult.match_id) \
        .add_columns(PlayerMatchResult.steamid, Match.match_uuid, Match.map, Match.mode,
                     Match.duration, Match.start_date) \
        .filter(PlayerMatchResult.steamid == steamid.as_64()).all()

    return jsonify({'matches': _matches_to_list(result)})


@app.route('/matches/list', methods=['GET', 'POST'])
def list_matches():
    result = Match.query.add_columns(PlayerMatchResult.steamid, Match.match_uuid, Match.map, Match.mode,
                     Match.duration, Match.start_date).all()
    return jsonify({'matches': _matches_to_list(result)})


@app.route('/player/matches/get/<match_uuid>', methods=['GET', 'POST'])
def get_matches_for_uuid(match_uuid):
    result = Match.query.filter(Match.match_uuid == match_uuid).one()
    if not result:
        return jsonify({
            'success': False
        })

    path = os.path.join(matches_folder, match_uuid)

    with open(path, 'rb') as f:
        z = zipfile.ZipFile(f)
        match_data = json.loads(z.read('stats.json').decode("utf-8"))

    return jsonify(match_data)
