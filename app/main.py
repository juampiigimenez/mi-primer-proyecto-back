"""
Main FastAPI application with modular architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)

# Import routers
from app.routers import imports

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(imports.router, prefix="/api/v1/imports", tags=["Imports"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])  # TODO: Next phase
# app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])  # TODO: Next phase
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])  # TODO: Next phase


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": API_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
