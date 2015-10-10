from sqlalchemy import Column, Integer, Float, BigInteger, String, Boolean, DateTime, ForeignKey
from .database import Base

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)

    submitter_ip = Column(String(150), nullable=False)

    # 32 byte uuid. Also identifies the filename in the matches folder.
    match_uuid = Column(String(32), unique=True, nullable=False)

    # Metadata of the match set at start
    start_date = Column(DateTime, nullable=False)
    mode = Column(String(150), nullable=False)
    map = Column(String(150), nullable=False)

    # Metadata set when match is finished
    duration = Column(Float)

class PlayerMatchResult(Base):
    """ Represents a match in which the player participated. """
    __tablename__ = 'player_match_results'
    id = Column(Integer, primary_key=True)
    steamid = Column(BigInteger, nullable=False)
    match_id = Column(Integer, ForeignKey(Match.id), nullable=False)
    # The Game Server creates the initial entries, the players must send a request to confirm they are in the match
    verified = Column(Boolean, nullable=False)
