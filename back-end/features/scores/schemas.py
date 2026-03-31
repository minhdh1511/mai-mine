from pydantic import BaseModel
from typing import Optional, List

class ScoreBase(BaseModel):
    song_name: str
    song_score: float
    internal_difficulty: float
    difficulty: str
    maimai_version: int
    achievement_status: str
    sync_status: str
    chart_mode: str
    song_jacket_url: str

# You only customise ScoreCreate when the data required to create
# a record is different from the standard data shared across the rest of the app (ScoreBase).
class ScoreCreate(ScoreBase):
    pass 

# The Response Schema: Used when sending data back to your frontend
class ScoreResponse(ScoreBase):
    id: int # The database will generate this, so we include it in the response

    class Config:
        # This tells Pydantic to read data even if it's an ORM model (SQLAlchemy)
        # instead of a standard Python dictionary.
        from_attributes = True

class ScoreSuccessResponse(BaseModel):
    id: int
    message: str

class BestFiftyResponse(BaseModel):
    best_35: List[ScoreResponse]
    best_15: List[ScoreResponse]
    total_best_35_rating: int
    total_best_15_rating: int
    total_rating: int