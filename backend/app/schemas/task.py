"""
Pydantic schemas for Task data validation and serialization.

These schemas define the data structures for creating, updating, and reading tasks
through the API. They ensure that data conforms to the expected format and types.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base schema for a Task, containing common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="The title of the task.")
    description: Optional[str] = Field(None, description="A detailed description of the task.")
    due_date: Optional[datetime] = Field(None, description="The due date for the task.")
    priority: Optional[str] = Field(None, description="The priority level of the task (e.g., 'High', 'Medium').")


class TaskCreate(TaskBase):
    """
    Schema used for creating a new task.
    Inherits all fields from TaskBase.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    All fields are optional, allowing for partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="The new title of the task.")
    description: Optional[str] = Field(None, description="The new description of the task.")
    completed: Optional[bool] = Field(None, description="The new completion status of the task.")
    due_date: Optional[datetime] = Field(None, description="The new due date for the task.")
    priority: Optional[str] = Field(None, description="The new priority level of the task.")


class TaskResponse(TaskBase):
    """
    Schema for representing a task in API responses.
    Includes all fields from the database model, including the ID and timestamps.
    """
    id: int = Field(..., description="The unique identifier of the task.")
    completed: bool = Field(..., description="The completion status of the task.")
    created_at: datetime = Field(..., description="The timestamp when the task was created.")
    updated_at: datetime = Field(..., description="The timestamp when the task was last updated.")
    
    class Config:
        """Pydantic configuration to allow mapping from ORM models."""
        from_attributes = True


class NaturalLanguageRequest(BaseModel):
    """Schema for the request to the natural language task parsing endpoint."""
    text: str = Field(..., min_length=1, description="The natural language text to be parsed into a task.")
    
    class Config:
        """Adds an example to the OpenAPI documentation for this schema."""
        json_schema_extra = {
            "example": {
                "text": "Remind me to submit taxes next Monday at noon"
            }
        }