from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uvicorn

from core.database import engine, Base, get_async_session

from features.scores.router import router as scores_router

# Lifespan event to create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # This creates the tables based on your models
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up the engine when the app shuts down
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# Allow your Angular frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], # Replace with your Angular port if different
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, PUT, DELETE
    allow_headers=["*"],
)

app.include_router(scores_router)

@app.get("/")
async def test_api():
    return {
        "message": "Hello World!"
    }

# A simple test route to verify the database connection
@app.get("/test-db")
async def test_database_connection(session: AsyncSession = Depends(get_async_session)):
    try:
        # Try to run a simple async query
        result = await session.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connected successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
