import os

from fastapi import FastAPI

from src.db.database import Base, init_database
from src.routers import auth, budget, expense

app: FastAPI = FastAPI(title="Expense Tracker API")

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
async def root():
    """Health check endpoint"""
    return {"message": "Expense Tracker API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {"status": "healthy"}
