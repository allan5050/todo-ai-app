"""Task API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, NaturalLanguageRequest
from app.services.task_service import TaskService
from app.services.llm_service import LLMService
from app.repositories.task_repository import TaskRepository
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependency to get task service."""
    repository = TaskRepository(db)
    return TaskService(repository)


def get_llm_service() -> LLMService:
    """Dependency to get LLM service."""
    return LLMService()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Create a new task."""
    try:
        logger.info(f"Creating task: {task.title}")
        created_task = service.create_task(task)
        return TaskResponse.model_validate(created_task)
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.post("/parse", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_from_natural_language(
    request: NaturalLanguageRequest,
    task_service: TaskService = Depends(get_task_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> TaskResponse:
    """Create a task from natural language description."""
    try:
        logger.info(f"Parsing natural language: {request.text}")
        
        # Parse natural language to task
        task_data = llm_service.parse_natural_language(request.text)
        
        # Create the task
        created_task = task_service.create_task(task_data)
        return TaskResponse.model_validate(created_task)
    except Exception as e:
        logger.error(f"Error creating task from natural language: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse natural language or create task"
        )


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service)
) -> List[TaskResponse]:
    """Get all tasks."""
    try:
        logger.info(f"Fetching tasks (skip={skip}, limit={limit})")
        tasks = service.get_tasks(skip=skip, limit=limit)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Get a specific task."""
    try:
        logger.info(f"Fetching task {task_id}")
        task = service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return TaskResponse.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch task"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Update a task."""
    try:
        logger.info(f"Updating task {task_id}")
        updated_task = service.update_task(task_id, task_update)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return TaskResponse.model_validate(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> None:
    """Delete a task."""
    try:
        logger.info(f"Deleting task {task_id}")
        success = service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )