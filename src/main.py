import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import config
from src.db.database import Base, init_database
from src.routers import auth, budget, expense

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)
app: FastAPI = FastAPI(title="Expense Tracker API")

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
origins = config.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(expense.router)
app.include_router(budget.router)

# Initialize database only if not in test environment
if not os.getenv("TEST_ENV"):
    # Initialize the database connection and create tables
    init_database()

    # Import models to ensure they are registered with Base

    # Create tables for non-test environments
    from src.db.database import engine
    if engine is not None:
        Base.metadata.create_all(bind=engine)

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Health check endpoint"""
    return {"message": "Expense Tracker API is running"}

@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint for load balancer"""
    return {"status": "healthy"}
