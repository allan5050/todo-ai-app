"""Task database model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

# The declarative base which our model will inherit from.
# All models mapping to database tables must be a subclass of this base.
Base = declarative_base()

class Task(Base):
    """
    Represents a single task in the database.
    
    This SQLAlchemy model maps to the 'tasks' table and defines the schema
    for storing all task-related information.
    """
    
    __tablename__ = "tasks"
    
    # --- Columns ---
    
    # The unique identifier for the task.
    id: int = Column(Integer, primary_key=True, index=True)
    
    # The title of the task, a brief summary.
    title: str = Column(String(255), nullable=False)
    
    # A more detailed description of the task. Optional.
    description: Optional[str] = Column(Text, nullable=True)
    
    # Flag indicating whether the task has been completed.
    completed: bool = Column(Boolean, default=False, nullable=False)
    
    # The date and time when the task is due. Optional.
    due_date: Optional[datetime] = Column(DateTime, nullable=True)
    
    # The priority of the task (e.g., 'High', 'Medium', 'Low'). Optional.
    priority: Optional[str] = Column(String(50), nullable=True)
    
    # Timestamp for when the task was created.
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamp for the last time the task was updated.
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the Task object."""
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"