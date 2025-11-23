"""
AI-Powered Form Filling API

Main application entry point for the FastAPI backend.
This API provides system monitoring and form filling capabilities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.v1 import v1_router
from api.v1.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    ALLOWED_ORIGINS,
    RATE_LIMIT_ENABLED,
    GLOBAL_RATE_LIMIT_REQUESTS,
    GLOBAL_RATE_LIMIT_PERIOD
)
from api.v1.middleware.rate_limiter import RateLimitMiddleware
from utils.logger import logger


# Initialize FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure global rate limiting (optional)
# Uncomment to enable global rate limiting across all endpoints
# if RATE_LIMIT_ENABLED:
#     app.add_middleware(
#         BaseHTTPMiddleware,
#         dispatch=RateLimitMiddleware(
#             max_requests=GLOBAL_RATE_LIMIT_REQUESTS,
#             window_seconds=GLOBAL_RATE_LIMIT_PERIOD
#         )
#     )
#     logger.info(
#         f"Global rate limiting enabled: "
#         f"{GLOBAL_RATE_LIMIT_REQUESTS} requests per {GLOBAL_RATE_LIMIT_PERIOD}s"
#     )

# Include API v1 router
app.include_router(v1_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    
    Returns basic API information and available endpoints.
    """
    return JSONResponse(
        content={
            "message": "Welcome to AI-Powered Form Filling API",
            "version": API_VERSION,
            "docs": "/docs",
            "health": "/v1/system/health"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info("API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info(f"Shutting down {API_TITLE}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )