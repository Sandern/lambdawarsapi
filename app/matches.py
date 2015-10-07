from flask import request, jsonify
from . import app
import uuid
import os
import zipfile
import json
from datetime import datetime

from valve.steam.id import SteamID
import bitstruct

from .database import db_session
from .models import Match, PlayerMatchResult

if not os.path.exists(app.instance_path):
    os.mkdir(app.instance_path)

matches_folder = os.path.join(app.instance_path, app.config['MATCHES_FOLDER'])
if not os.path.exists(matches_folder):
    os.mkdir(matches_folder)


def build_steamid(steamid_unparsed):
    if steamid_unparsed.isdigit():
        universe, type, instance, account_number = bitstruct.unpack('u8u4u20u32',
                             bitstruct.pack('u64', int(steamid_unparsed)))

        if instance == 1:
            instance = 0
            account_number = int(account_number / 2)

        return SteamID(account_number, instance, type, universe)


    id = SteamID.from_text(steamid_unparsed)
    return id

@app.route('/matches/upload', methods=['POST'])
def upload_file():
    """ Records a match result from a game server. """
    f = request.files['match_data']

    # Create the match id
    match_uuid = uuid.uuid4().hex

    # Read the file as json
    # Could be too large? Probably not, but maybe.
    z = zipfile.ZipFile(f.stream)
    match_data = json.loads(z.read('stats.json').decode("utf-8"))

    # Create the match entry
    m_entry = Match()
    m_entry.start_date = datetime.strptime(match_data['start_date'],'%Y-%m-%d %H:%M:%S')
    m_entry.duration = match_data['duration']
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

        db_session.add(p_entry)

    db_session.commit()

    # Save the match file
    path = os.path.join(matches_folder, match_uuid)

    f.stream.seek(0)
    f.save(path)

    return jsonify(success=True)

@app.route('/player/matches/list/<steamid>', methods=['GET', 'POST'])
def list_matches_for_steamid(steamid):
    """ Lists the match history for a player. """
    steamid = build_steamid(steamid)

    result = Match.query.join(PlayerMatchResult, Match.id == PlayerMatchResult.match_id) \
        .add_columns(PlayerMatchResult.steamid, Match.match_uuid, Match.map, Match.mode,
                     Match.duration, Match.start_date) \
        .filter(PlayerMatchResult.steamid == steamid.as_64()).all()

    response = {'matches': []}
    for r in result:
        response['matches'].append({
            'steamid': r.steamid,
            'match_uuid': r.match_uuid,
            'duration': r.duration,
            'start_date': r.start_date,
            'mode': r.mode,
            'map': r.map,
        })

    return jsonify(response)

@app.route('/player/matches/get/<match_uuid>', methods=['GET', 'POST'])
def get_matches_for_uuid(match_uuid):
    result = Match.query.filter(Match.match_uuid == match_uuid).one()

    path = os.path.join(matches_folder, match_uuid)

    with open(path, 'rb') as f:
        z = zipfile.ZipFile(f)
        match_data = json.loads(z.read('stats.json').decode("utf-8"))

    return jsonify(match_data)