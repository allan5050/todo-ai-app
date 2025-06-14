"""Task repository for database operations."""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


class TaskRepository:
    """Repository for task database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        try:
            logger.debug(f"Creating task with data: {task_data.model_dump()}")
            task = Task(**task_data.model_dump())
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            logger.info(f"Created task with id: {task.id}")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Error creating task: {str(e)}")
            self.db.rollback()
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination."""
        try:
            logger.debug(f"Fetching tasks with skip={skip}, limit={limit}")
            tasks = self.db.query(Task).offset(skip).limit(limit).all()
            logger.debug(f"Found {len(tasks)} tasks")
            return tasks
        except SQLAlchemyError as e:
            logger.error(f"Error fetching tasks: {str(e)}")
            raise
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        try:
            logger.debug(f"Fetching task with id: {task_id}")
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if task:
                logger.debug(f"Found task: {task.title}")
            else:
                logger.debug(f"Task with id {task_id} not found")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}")
            raise
    
    def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        try:
            logger.debug(f"Updating task {task_id} with data: {task_data.model_dump(exclude_unset=True)}")
            task = self.get_by_id(task_id)
            if not task:
                return None
            
            update_data = task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)
            
            self.db.commit()
            self.db.refresh(task)
            logger.info(f"Updated task {task_id}")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def delete(self, task_id: int) -> bool:
        """Delete a task."""
        try:
            logger.debug(f"Deleting task with id: {task_id}")
            task = self.get_by_id(task_id)
            if not task:
                return False
            
            self.db.delete(task)
            self.db.commit()
            logger.info(f"Deleted task {task_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            self.db.rollback()
            raise