import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, edit
from app.core.config import settings
from app.api.v1.endpoints import analysis, health
from app.db.mongodb import close_mongo_connection, connect_to_mongo

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered contract risk detection system",
    version=settings.VERSION,
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])
app.include_router(edit.router, prefix="/api/v1/edit", tags=["editing"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])


@app.on_event("startup")
async def on_startup():
    try:
        await connect_to_mongo()
        logger.info("✅ MongoDB connected")
    except Exception as exc:
        # Keep app available for non-auth features if Mongo is temporarily unavailable
        logger.warning(f"⚠️ MongoDB connection failed at startup: {exc}")


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return {"message": "OK"}

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }