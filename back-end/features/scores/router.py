from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import List
import features.scores.utils as utils

from core.database import get_async_session
import features.scores.models as models
import features.scores.schemas as schemas

# This prefix applies to all routes in this file
router = APIRouter(prefix="/scores", tags=["Scores"])

CURRENT_MAIMAI_VERSION = 26

# ---------------------------------------------------------
# 1. GET ALL SCORES (Sorted by ratings descending)
# Endpoint: GET /scores
# ---------------------------------------------------------
@router.get("", response_model=List[schemas.ScoreResponse])
async def get_all_scores(
    skip: int = Query(0, description="How many records to skip"),
    limit: int = Query(50, description="How many records to return"),
    session: AsyncSession = Depends(get_async_session)
):
    # Added .order_by(desc(models.Score.ratings)) right before offset
    query = select(models.Score).order_by(desc(models.Score.ratings)).offset(skip).limit(limit)
    result = await session.execute(query)
    
    return result.scalars().all()

# ---------------------------------------------------------
# 2. GET BEST FIFTY (Split into B35 and B15)
# Endpoint: GET /scores/b50
# ---------------------------------------------------------
@router.get("/b50", response_model=schemas.BestFiftyResponse)
async def get_best_fifty(session: AsyncSession = Depends(get_async_session)):
    b35_query = select(models.Score).where(
        models.Score.maimai_version < CURRENT_MAIMAI_VERSION
    ).order_by(desc(models.Score.ratings)).limit(35)
    
    b35_result = await session.execute(b35_query)
    best_35 = b35_result.scalars().all()

    b15_query = select(models.Score).where(
        models.Score.maimai_version == CURRENT_MAIMAI_VERSION
    ).order_by(desc(models.Score.ratings)).limit(15)
    
    b15_result = await session.execute(b15_query)
    best_15 = b15_result.scalars().all()

    return {
        "best_35": best_35,
        "best_15": best_15,
        "total_best_35_rating": sum(score.ratings for score in best_35),
        "total_best_15_rating": sum(score.ratings for score in best_15),
        "total_rating": sum(score.ratings for score in best_35) + sum(score.ratings for score in best_15)
    }

# ---------------------------------------------------------
# 3. GET SPECIFIC SCORE BY ID
# Endpoint: GET /scores/{score_id}
# ---------------------------------------------------------
@router.get("/{score_id}", response_model=schemas.ScoreResponse)
async def get_score(score_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(models.Score).where(models.Score.id == score_id)
    result = await session.execute(query)
    score = result.scalars().first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
        
    return score

# ---------------------------------------------------------
# 4. CREATE NEW SCORE
# Endpoint: POST /scores
# ---------------------------------------------------------
@router.post("", response_model=schemas.ScoreSuccessResponse)
async def create_score(score_in: schemas.ScoreCreate, session: AsyncSession = Depends(get_async_session)):
    # Convert the Pydantic schema into a dictionary so we can modify it
    score_data = score_in.model_dump()
    
    # 2. CALL YOUR LOGIC HERE!
    # Calculate the missing fields based on the user's input
    calculated_rank = utils.calculate_song_rank(score_data["song_score"])
    calculated_rating = utils.calculate_rating(score_data["song_score"], score_data["internal_difficulty"])
    
    # 3. Inject your calculated values into the data before saving
    score_data["song_rank"] = calculated_rank
    score_data["ratings"] = calculated_rating
    
    # Create the database model with the updated data
    new_score = models.Score(**score_data)
    
    session.add(new_score)
    await session.commit()
    await session.refresh(new_score)
    
    return {
        "id": new_score.id,
        "message": f"Successfully added {new_score.song_name} to database."
    }

# ---------------------------------------------------------
# 5. UPDATE SCORE
# Endpoint: PUT /scores/{score_id}
# ---------------------------------------------------------
@router.put("/{score_id}", response_model=schemas.ScoreSuccessResponse)
async def update_score(
    score_id: int, 
    update_data: schemas.ScoreCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    query = select(models.Score).where(models.Score.id == score_id)
    result = await session.execute(query)
    existing_score = result.scalars().first()

    if not existing_score:
        raise HTTPException(status_code=404, detail="Score not found. Cannot update.")

    updated = False

    if update_data.song_score > existing_score.song_score:
        existing_score.song_score = update_data.song_score
        updated = True
        
    if update_data.song_rank != existing_score.song_rank: 
        existing_score.song_rank = update_data.song_rank
        updated = True

    if update_data.internal_difficulty != existing_score.internal_difficulty:
        existing_score.internal_difficulty = update_data.internal_difficulty
        updated = True

    if update_data.ratings > existing_score.ratings:
        existing_score.ratings = update_data.ratings
        updated = True

    if updated:
        existing_score.date_added = datetime.now()
        await session.commit()
        return {"id": existing_score.id, "message": "Score successfully updated with new personal bests!"}
    
    return {"id": existing_score.id, "message": "No updates made. Existing score was higher or equal."}

# ---------------------------------------------------------
# 6. DELETE SCORE
# Endpoint: DELETE /scores/{score_id}
# ---------------------------------------------------------
@router.delete("/{score_id}")
async def delete_score(score_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(models.Score).where(models.Score.id == score_id)
    result = await session.execute(query)
    score_to_delete = result.scalars().first()

    if not score_to_delete:
        raise HTTPException(status_code=404, detail="Score not found")

    await session.delete(score_to_delete)
    await session.commit()
    
    return {"message": "Score successfully deleted."}