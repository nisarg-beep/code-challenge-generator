from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import challenge, webhooks
# Import the engine and Base to handle database initialization
from .database.base import engine, Base
# Import models so SQLAlchemy knows which tables to create
from .database import models

# This command tells SQLAlchemy to create all tables (and new columns)
# defined in models.py using the engine from base.py
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(challenge.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")