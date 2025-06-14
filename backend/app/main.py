"""
Main entry point for the FastAPI application.

This module initializes the FastAPI application, configures middleware,
sets up event handlers, and includes the API routers.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings, logger
from app.database import init_db
from app.api.endpoints import tasks
from app.api.endpoints import health

# Initialize FastAPI app
app = FastAPI(
    title="Todo AI App",
    description="A Todo/Task-List application with natural language task creation powered by an LLM.",
    version="1.0.0",
    debug=settings.debug,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    This function is called once when the application starts.
    It's used here to initialize the database tables.
    """
    logger.info("Starting up the Todo AI application...")
    try:
        init_db()
        logger.info("Application startup was successful.")
    except Exception as e:
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        raise


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing basic information about the API.
    """
    return {
        "message": "Welcome to the Todo AI App API",
        "version": app.version,
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler to catch any unhandled exceptions.
    This ensures that the server returns a generic 500 error response
    instead of crashing.
    """
    logger.error(f"Unhandled exception during request to {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )


# Include routers
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Running application in development mode with Uvicorn.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)