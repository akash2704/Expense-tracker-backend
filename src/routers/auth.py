import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.models.user import User as UserModel
from src.repositories.users_repo import create_user, get_user_by_username
from src.schemas.users import Token, User, UserCreate
from src.services.auth_service import (
    create_access_token,
    get_password_hash,
    verify_password,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)) -> User:
    logger.info("Registering user: %s with session: %s, engine: %s", user.username, id(db), id(db.bind))
    db_user: UserModel | None = get_user_by_username(db, user.username)
    if db_user:
        logger.warning("Username already registered: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already registered")
    logger.info("Creating new user: %s", user.username)
    hashed_password: str = get_password_hash(user.password)
    new_user: UserModel = UserModel(username=user.username, hashed_password=hashed_password)
    return create_user(db, new_user, user.initial_bank, user.initial_cash)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict[str, str]:
    logger.info("Login attempt for user: %s with session: %s, engine: %s", form_data.username, id(db), id(db.bind))
    user: UserModel | None = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed for user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Login successful for user: %s", form_data.username)
    access_token: str = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
