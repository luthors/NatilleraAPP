"""
Natillera Backend - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Natillera API",
    description="API for Natillera App - Colombian Savings Group Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (will be added as we build endpoints)
# from app.api.v1.router import api_router
# app.include_router(api_router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Welcome to Natillera API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "ok"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
