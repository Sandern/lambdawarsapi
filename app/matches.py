from flask import request, jsonify
from sqlalchemy.orm.exc import NoResultFound
from . import app
import uuid
import os
import zipfile
import json
from datetime import datetime

from .util import build_steamid, authenticate_ticket, validate_uuid4
from .database import db
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
    m_entry.type = match_data['type']
    m_entry.match_uuid = match_uuid

    db.session.add(m_entry)
    db.session.commit()

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

        db.session.add(p_entry)

    db.session.commit()

    return jsonify(success=True, match_uuid=match_uuid)


@app.route('/matches/verify_player', methods=['POST'])
def verify_player():
    auth_ticket = request.form.get("auth_ticket")
    match_uuid = request.form.get("match_uuid")

    steamid = authenticate_ticket(auth_ticket)
    if not steamid:
        return jsonify(success=False)

    m_entry = Match.query.filter(Match.match_uuid == match_uuid).one()

    result = PlayerMatchResult.query.filter(PlayerMatchResult.steamid == steamid.as_64(),
                                            PlayerMatchResult.match_id == m_entry.id).one()

    result.verified = True
    db.session.commit()

    return jsonify(success=True)


def _find_player_data(players, steamid):
    for owner, data in players.items():
        if 'steamid' not in data:
            continue

        player_steamid = build_steamid(data['steamid'])
        if player_steamid.as_64() == steamid.as_64():
            return data, owner

    return None, -1


@app.route('/matches/upload', methods=['POST'])
def record_match_end():
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

    # Update end state of each player
    players = match_data.get('players', {})
    #losers = map(int, match_data.get('losers', []))
    winners = map(int, match_data.get('winners', []))

    player_results = PlayerMatchResult.query.filter(PlayerMatchResult.match_id == m_entry.id)
    for pr in player_results:
        steamid = build_steamid(pr.steamid)
        player_data, owner = _find_player_data(players, steamid)
        if not player_data:
            continue

        pr.end_state = 'won' if int(owner) in winners else 'lost'

    db.session.commit()

    # Save the match file
    path = os.path.join(matches_folder, match_uuid)

    f.stream.seek(0)
    f.save(path)

    return jsonify(success=True)


def _matches_to_list(result):
    matches = []
    for r in result:
        matches.append({
            'match_uuid': r.match_uuid,
            'duration': r.duration,
            'start_date': r.start_date,
            'mode': r.mode,
            'map': r.map,
            'type': r.type,
        })
        if hasattr(r, 'steamid'):
            matches[-1]['steamid'] = r.steamid
            matches[-1]['verified'] = r.verified
            matches[-1]['end_state'] = r.end_state
    return matches


@app.route('/player/matches/list/<steamid>/<page>', methods=['GET', 'POST'])
def list_matches_for_steamid(steamid, page):
    """ Lists the match history for a player. """
    steamid = build_steamid(steamid)
    page = int(page)
    per_page = int(request.values.get('per_page', app.config['MAX_MATCHES_PER_PAGE']))

    p = Match.query.join(PlayerMatchResult, Match.id == PlayerMatchResult.match_id) \
        .add_columns(PlayerMatchResult.steamid, Match.match_uuid, Match.map, Match.mode, Match.type,
                     Match.duration, Match.start_date, PlayerMatchResult.verified,
                     PlayerMatchResult.end_state) \
        .filter(PlayerMatchResult.steamid == steamid.as_64()) \
        .order_by(Match.start_date.desc()) \
        .paginate(page, per_page, False)

    return jsonify({
        'matches': _matches_to_list(p.items),
        'total': p.total,
        'per_page': p.per_page,
        'page': p.page,
    })


@app.route('/player/matches/list/<steamid>', methods=['GET', 'POST'])
def list_matches_for_steamid_first_page(steamid):
    return list_matches_for_steamid(steamid, 1)


@app.route('/matches/list/<page>', methods=['GET', 'POST'])
def list_matches(page):
    page = int(page)
    per_page = int(request.values.get('per_page', app.config['MAX_MATCHES_PER_PAGE']))

    p = Match.query.add_columns(Match.match_uuid, Match.map, Match.mode, Match.type,
                     Match.duration, Match.start_date) \
                    .order_by(Match.start_date.desc()) \
                    .paginate(page, per_page, False)

    return jsonify({
        'matches': _matches_to_list(p.items),
        'total': p.total,
        'per_page': p.per_page,
        'page': p.page,
    })


@app.route('/matches/list', methods=['GET', 'POST'])
def list_matches_first_page():
    return list_matches(1)


@app.route('/player/matches/get/<match_uuid>', methods=['GET', 'POST'])
def get_matches_for_uuid(match_uuid):
    if not validate_uuid4(match_uuid):
        return jsonify({
            'success': False,
            'error_msg': 'match uuid is not valid',
        })

    try:
        Match.query.filter(Match.match_uuid == match_uuid).one()
    except NoResultFound:
        return jsonify({
            'success': False,
            'error_msg': 'no match exists with given uuid',
        })

    path = os.path.join(matches_folder, match_uuid)

    with open(path, 'rb') as f:
        z = zipfile.ZipFile(f)
        match_data = json.loads(z.read('stats.json').decode("utf-8"))

    return jsonify(match_data)
