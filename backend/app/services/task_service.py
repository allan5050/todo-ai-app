"""Task service for business logic."""
import logging
from typing import List, Optional

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """Service layer for task operations."""
    
    def __init__(self, repository: TaskRepository):
        """Initialize service with repository."""
        self.repository = repository
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        logger.info(f"Creating task: {task_data.title}")
        return self.repository.create(task_data)
    
    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks."""
        logger.info(f"Fetching tasks (skip={skip}, limit={limit})")
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        logger.info(f"Fetching task {task_id}")
        return self.repository.get_by_id(task_id)
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        logger.info(f"Updating task {task_id}")
        return self.repository.update(task_id, task_data)
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        logger.info(f"Deleting task {task_id}")
        return self.repository.delete(task_id)