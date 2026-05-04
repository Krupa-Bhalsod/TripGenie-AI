from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.models.user_model import UserRegister, UserLogin, UserResponse, UserDB, User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from app.db.sqlite import get_db
from datetime import timedelta
from app.core.config import settings
from app.core.exceptions import APIError
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email {user.email} already exists.")
        raise APIError(
            user_message="Email already registered",
            exception_string="DuplicateKeyError",
            message=f"Email {user.email} is already taken.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        preferences={}
    )
    
    # Save to SQLite
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Successfully registered new user: {db_user.email}")
    
    # Return user response (without password)
    return UserResponse(
        name=db_user.name,
        email=db_user.email,
        preferences=db_user.preferences
    )

@router.post("/login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_credentials.email).first()
    if not db_user:
        logger.warning(f"Login failed: Incorrect email {user_credentials.email}")
        raise APIError(
            user_message="Incorrect email or password",
            exception_string="AuthError",
            message="User not found with provided email.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    if not verify_password(user_credentials.password, db_user.password_hash):
        logger.warning(f"Login failed: Incorrect password for {db_user.email}")
        raise APIError(
            user_message="Incorrect email or password",
            exception_string="AuthError",
            message="Password verification failed.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    logger.info(f"User {db_user.email} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        name=current_user.name,
        email=current_user.email,
        preferences=current_user.preferences
    )
