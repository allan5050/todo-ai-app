"""API endpoints for managing tasks."""
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

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={404: {"description": "Not found"}}
)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """
    FastAPI dependency to create and provide a TaskService instance.
    This creates a new repository and service for each request, ensuring
    session safety in a threaded environment.
    """
    repository = TaskRepository(db)
    return TaskService(repository)


def get_llm_service() -> LLMService:
    """
    FastAPI dependency to create and provide an LLMService instance.
    """
    return LLMService()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """
    Create a new task from structured data.
    
    - **task**: The task data to create.
    """
    try:
        logger.info(f"Received request to create task: {task.title}")
        created_task = service.create_task(task)
        return TaskResponse.model_validate(created_task)
    except Exception as e:
        logger.error(f"Error during task creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the task."
        )


@router.post("/parse", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_from_natural_language(
    request: NaturalLanguageRequest,
    task_service: TaskService = Depends(get_task_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> TaskResponse:
    """
    Create a new task by parsing a natural language description.
    This endpoint uses the LLM service to interpret the text and then creates a task.
    
    - **request**: The natural language text to parse.
    """
    try:
        logger.info(f"Received request to parse natural language: '{request.text}'")
        
        # 1. Parse the natural language input into a structured TaskCreate schema.
        #    The LLM service will sanitize inappropriate content internally.
        task_data = llm_service.parse_natural_language(request.text, request.timezone)
        
        # 2. Use the standard task creation service to save the new task.
        created_task = task_service.create_task(task_data)
        return TaskResponse.model_validate(created_task)
    except Exception as e:
        logger.error(f"Error during natural language task creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse natural language or create task."
        )


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service)
) -> List[TaskResponse]:
    """
    Retrieve a list of all tasks with pagination.
    
    - **skip**: Number of tasks to skip from the start.
    - **limit**: Maximum number of tasks to return.
    """
    try:
        logger.info(f"Received request to fetch tasks (skip={skip}, limit={limit})")
        tasks = service.get_tasks(skip=skip, limit=limit)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks."
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """
    Retrieve a single task by its ID.
    
    - **task_id**: The unique identifier of the task to retrieve.
    """
    try:
        logger.info(f"Received request to fetch task {task_id}")
        task = service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        return TaskResponse.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch task."
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """
    Update an existing task.
    
    - **task_id**: The ID of the task to update.
    - **task_update**: The fields to update in the task.
    """
    try:
        logger.info(f"Received request to update task {task_id}")
        updated_task = service.update_task(task_id, task_update)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        return TaskResponse.model_validate(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task."
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> None:
    """
    Delete a task by its ID.
    
    - **task_id**: The ID of the task to delete.
    """
    try:
        logger.info(f"Received request to delete task {task_id}")
        success = service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task."
        )