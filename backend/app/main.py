from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import edit
from app.core.config import settings
from app.api.v1.endpoints import analysis, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered contract risk detection system",
    version=settings.VERSION,
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])
app.include_router(edit.router, prefix="/api/v1/edit", tags=["editing"])

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