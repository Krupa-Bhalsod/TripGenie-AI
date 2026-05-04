from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.sqlite import engine, Base
from app.api.auth_routes import router as auth_router
from app.api.trip_routes import router as trip_router
from app.core.exceptions import APIError
from app.core.logger import get_logger

# Create database tables
Base.metadata.create_all(bind=engine)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting TripGenie AI API")
    yield
    # Shutdown
    logger.info("👋 Shutting down TripGenie AI API")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    logger.error(f"APIError: {exc.exception_string} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "user_message": exc.user_message,
            "error": exc.message,
            "details": exc.exception_string
        }
    )

# Set up CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(trip_router, prefix="/trip", tags=["Trip Planning"])

@app.get("/")
async def root():
    return {"message": "Welcome to TripGenie AI API"}
