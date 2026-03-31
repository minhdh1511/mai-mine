from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func # Import this to get the database's current time
from core.database import Base

class Score(Base): 
    __tablename__ = 'scores'

    id = Column(Integer, primary_key = True, index = True)

    song_name = Column(String, index = True)
    song_score = Column(Float)
    song_rank = Column(String)
    internal_difficulty = Column(Float)
    difficulty = Column(String)
    maimai_version = Column(Integer, index = True)
    ratings = Column(Integer)
    achievement_status = Column(String)
    sync_status = Column(String)
    date_added = Column(DateTime(timezone = True), server_default = func.now())
    chart_mode = Column(String)
    song_jacket_url = Column(String)