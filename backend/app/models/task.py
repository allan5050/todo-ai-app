"""Task database model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    """Task model for database storage."""
    
    __tablename__ = "tasks"
    
    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    completed: bool = Column(Boolean, default=False, nullable=False)
    due_date: Optional[datetime] = Column(DateTime, nullable=True)
    priority: Optional[str] = Column(String(50), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of Task."""
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"