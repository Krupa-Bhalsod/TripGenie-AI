from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user_model import UserRegister, UserLogin, UserResponse, UserDB
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from app.db.mongodb import mongodb
from datetime import timedelta
from app.core.config import settings
from app.core.exceptions import APIError
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    # Check if user already exists
    existing_user = await mongodb.db["users"].find_one({"email": user.email})
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
    user_db = UserDB(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    
    # Save to MongoDB
    await mongodb.db["users"].insert_one(user_db.model_dump())
    logger.info(f"Successfully registered new user: {user.email}")
    
    # Return user response (without password)
    return UserResponse(
        name=user_db.name,
        email=user_db.email,
        preferences=user_db.preferences
    )

@router.post("/login")
async def login(user_credentials: UserLogin):
    user_dict = await mongodb.db["users"].find_one({"email": user_credentials.email})
    if not user_dict:
        logger.warning(f"Login failed: Incorrect email {user_credentials.email}")
        raise APIError(
            user_message="Incorrect email or password",
            exception_string="AuthError",
            message="User not found with provided email.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user = UserDB(**user_dict)
    if not verify_password(user_credentials.password, user.password_hash):
        logger.warning(f"Login failed: Incorrect password for {user_credentials.email}")
        raise APIError(
            user_message="Incorrect email or password",
            exception_string="AuthError",
            message="Password verification failed.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"User {user.email} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return UserResponse(
        name=current_user.name,
        email=current_user.email,
        preferences=current_user.preferences
    )
