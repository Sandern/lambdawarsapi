from .database import db

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)

    submitter_ip = db.Column(db.String(150), nullable=False)

    # 32 byte uuid. Also identifies the filename in the matches folder.
    match_uuid = db.Column(db.String(32), unique=True, nullable=False)

    # Metadata of the match set at start
    start_date = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(150), nullable=False)
    map = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(150), nullable=False)

    # Metadata set when match is finished
    duration = db.Column(db.Float)

class PlayerMatchResult(db.Model):
    """ Represents a match in which the player participated. """
    __tablename__ = 'player_match_results'
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.BigInteger, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id), nullable=False)
    # The Game Server creates the initial entries, the players must send a request to confirm they are in the match
    verified = db.Column(db.Boolean, nullable=False)
    # End state of this player (won, lost, draw). As string so we could have more states later.
    end_state = db.Column(db.String(150))