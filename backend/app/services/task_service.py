"""
Task service for business logic.

This module contains the service layer for task-related operations. It uses the
TaskRepository to interact with the database and encapsulates the core business
logic for managing tasks.
"""
import logging
from typing import List, Optional

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """
    Service layer for task operations.
    
    This class contains the business logic for managing tasks. It acts as an
    intermediary between the API layer and the data access layer (repository).
    """
    
    def __init__(self, repository: TaskRepository):
        """
        Initializes the TaskService with a task repository.
        
        Args:
            repository: An instance of TaskRepository for data access.
        """
        self.repository = repository
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Orchestrates the creation of a new task.
        
        Args:
            task_data: The data for the new task.
            
        Returns:
            The created Task object.
        """
        logger.info(f"Creating task: {task_data.title}")
        return self.repository.create(task_data)
    
    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Retrieves a paginated list of all tasks.
        
        Args:
            skip: Number of tasks to skip.
            limit: Maximum number of tasks to return.
            
        Returns:
            A list of Task objects.
        """
        logger.info(f"Fetching tasks (skip={skip}, limit={limit})")
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieves a single task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            
        Returns:
            The Task object if found, otherwise None.
        """
        logger.info(f"Fetching task {task_id}")
        return self.repository.get_by_id(task_id)
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """
        Orchestrates the update of an existing task.
        
        Args:
            task_id: The ID of the task to update.
            task_data: The data to update the task with.
            
        Returns:
            The updated Task object, or None if the task was not found.
        """
        logger.info(f"Updating task {task_id}")
        return self.repository.update(task_id, task_data)
    
    def delete_task(self, task_id: int) -> bool:
        """
        Orchestrates the deletion of a task.
        
        Args:
            task_id: The ID of the task to delete.
            
        Returns:
            True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting task {task_id}")
        return self.repository.delete(task_id)