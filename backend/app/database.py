"""
Database configuration and session management for the application.

This module sets up the SQLAlchemy engine and session factory. It also provides
a dependency (`get_db`) for use in FastAPI routes to obtain a database session,
and a utility function (`init_db`) to create database tables.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.models.task import Base

logger = logging.getLogger(__name__)

# The SQLAlchemy engine is the starting point for any SQLAlchemy application.
# It's a factory for database connections and provides a connection pool.
engine = create_engine(
    settings.database_url,
    # This argument is specific to SQLite and is required for it to work correctly
    # with FastAPI's single-threaded async environment.
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# SessionLocal is a factory for creating new Session objects.
# It's configured to not autocommit or autoflush, giving us fine-grained
# control over transaction management within our repository layer.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initializes the database by creating all tables defined in the Base metadata.
    This is typically called once at application startup.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def get_db() -> Session:
    """
    A FastAPI dependency that provides a transactional database session.
    
    This function yields a new database session for each request that needs it,
    and ensures that the session is closed after the request is finished,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()