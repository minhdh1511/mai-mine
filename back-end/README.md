0. Set up a new project (for FastAPI)
- Install python
- Install uv (brew install uv)
- Initialise the project with (uv init .)
- Install fastapi (uv add fastapi)
- Install python-dotenv (uv add python-dotenv)
- Install sqlalchemy for database and authen/autho (uv add "fastapi-users[sqlalchemy]")
- Install aiosqlite for interacting with the database (asynchronously)
- Install uvicorn as a web server for serving FastAPI application (uv add "uvicorn[standard]")
- Install alembic for database migration tool (uv add alembic)

- IMPORTANT: To run any tool that you installed via uv later on, put "uv run" before the command!

1. Project structure for this app

mai-mine-BE/
├── .env                    # Your environment variables (database URL, secret keys)
├── main.py                 # The entry point for your FastAPI application
├── core/                   # App-wide settings and configurations
│   ├── config.py           # Loads variables from .env
│   └── database.py         # SQLAlchemy engine and session setup
└── features/               # Your modular feature folders
    ├── auth/               # (For your fastapi-users integration later)
    │   ├── router.py       # API endpoints (e.g., POST /login)
    │   ├── schemas.py      # Pydantic models (data validation for requests/responses)
    │   └── models.py       # SQLAlchemy models (the database tables)
    └── songs/              # Your maimai B50 song feature
        ├── router.py       
        ├── schemas.py      
        ├── models.py       
        └── crud.py         # Database operations (Create, Read, Update, Delete)

2. Workflow
- Define the model
- Define the database schema (Data Transfer Objects (DTOs))
- Define the controllers (API endpoints)

3. API response customisation
- Customise the "shape" of the response in the schemas.py 
- Customise the actual data that gets returned in the router's return statement

4. Setup for other people to clone the code
- Install git
- Install python
- pip install uv
- Create .env and then put the DATABASE_URL in there 
- Go into back-end folder and "uv sync"
- Run the back-end app "uv run main.py"

5. Set up monorepo (if the app contains both back-end and front-end folder)
- mkdir <app_name>
- cd <app_name>
- git init (Do this immediately from the get-go!)
- Then we create the front-end and the back-end folders by initialising the FE/BE app
- ng new front-end --skip-git (Angular app, skips git)
- uv init back-end (uv skip git initialisation because we already ran git init from the beginning)
- If both apps from the beginning already set up .git then simply remove the .git from both of those folders
and then go to the root folder and do "git init"

6. Migrate the datebase to a newer version in case the models change (set up from scratch)
- Set up core/database.py file with your async engine (if setting up a new project)
- Write your first models.py (if setting up a new project, can just be a simple User table to get started)
- "uv add alembic" if you have not already
- To run alembic commands that is installed via uv you have to add "uv run" at the start of the command
- Run "uv run alembic init -t async alembic" to initialise the async template for our async setup
(an alembic.ini and an alembic/ folder will appear upon executing)
- Configure the alembic/env.py file to connect alembic to our app

```
import asyncio
from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Add your project root to the path so Alembic can find your files
sys.path.insert(0, os.path.realpath('.'))

# 2. Load your environment variables (.env)
load_dotenv()

# 3. Import your Base and Models
from core.database import Base
# You MUST import your models here so Alembic can see them!
import features.scores.models

# this is the Alembic Config object
config = context.config

# 4. Override the sqlalchemy.url in alembic.ini with the one from your .env
config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. Set the target metadata
target_metadata = Base.metadata

# ... keep the rest of the file (run_migrations_offline and run_migrations_online) exactly as is ...
```

- Run uv run alembic revision --autogenerate -m "<your_message>"

- Apply it using uv run alembic upgrade head (will create DB if there's no DB)

- Next time if you wanna change or add a new feature just repeat:
>>> uv run alembic revision --autogenerate -m "<your_message>"
>>> uv run alembic upgrade head

- NOTE: 
   + If we add a new column to the model, then that same attribute in the schemas file must be Optional
   because the old data might not have that column
   + If we delete a column then that attribute will be gotten rid of entirely. Just like removing a whole Excel column!