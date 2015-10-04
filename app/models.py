from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from .database import Base

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)

    submitter_steamid = Column(BigInteger)
    submitter_verified = Column(Boolean)

    # 32 byte uuid. Also identifies the filename in the matches folder.
    match_uuid = Column(String(32), unique=True)

    # Metadata of the match
    mode = Column(String(150))
    map = Column(String(150))

class PlayerMatchResult(Base):
    """ Represents a match in which the player participated. """
    __tablename__ = 'player_match_results'
    id = Column(Integer, primary_key=True)
    steamid = Column(BigInteger)
    match_id = Column(Integer, ForeignKey(Match.id), nullable=False)