"""Task schemas for API validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    priority: Optional[str] = Field(None, description="Task priority")


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NaturalLanguageRequest(BaseModel):
    """Schema for natural language task creation."""
    text: str = Field(..., min_length=1, description="Natural language description of the task")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Remind me to submit taxes next Monday at noon"
            }
        }