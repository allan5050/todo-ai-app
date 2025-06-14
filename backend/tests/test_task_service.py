"""
Tests for the TaskService.

To run these tests, navigate to the `backend` directory, activate your virtual
environment, and then run `pytest`.

Example using PowerShell:
```powershell
cd backend
.\\venv\\Scripts\\Activate.ps1
pytest tests/test_task_service.py
```

Make sure you have the required packages installed from `requirements.txt`.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task

class TestTaskService:
    """A suite of tests for the TaskService class."""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """
        Pytest fixture to create a mock of the TaskRepository.
        This allows us to test the service layer in isolation.
        """
        return Mock(spec=TaskRepository)

    @pytest.fixture
    def task_service(self, mock_repository: Mock) -> TaskService:
        """
        Pytest fixture to create an instance of the TaskService,
        injecting the mock repository.
        """
        return TaskService(mock_repository)

    def test_create_task(self, task_service: TaskService, mock_repository: Mock):
        """
        Tests that the create_task service method correctly calls the
        repository's create method and returns the result.
        """
        # Arrange: Set up the input data and the expected return value from the mock repository.
        task_data = TaskCreate(title="Test Task", description="Test Description")
        expected_task = Task(id=1, title="Test Task", description="Test Description", completed=False)
        mock_repository.create.return_value = expected_task

        # Act: Call the service method.
        result = task_service.create_task(task_data)

        # Assert: Check that the result is correct and the repository was called properly.
        assert result == expected_task
        mock_repository.create.assert_called_once_with(task_data)

    def test_get_tasks(self, task_service: TaskService, mock_repository: Mock):
        """
        Tests that the get_tasks service method correctly calls the
        repository's get_all method with the right parameters.
        """
        # Arrange
        expected_tasks = [Task(id=1, title="Task 1"), Task(id=2, title="Task 2")]
        mock_repository.get_all.return_value = expected_tasks

        # Act
        result = task_service.get_tasks(skip=0, limit=100)

        # Assert
        assert result == expected_tasks
        mock_repository.get_all.assert_called_once_with(skip=0, limit=100)

    def test_get_task_by_id(self, task_service: TaskService, mock_repository: Mock):
        """
        Tests that the get_task service method correctly calls the
        repository's get_by_id method.
        """
        # Arrange
        task_id = 1
        expected_task = Task(id=task_id, title="Test Task")
        mock_repository.get_by_id.return_value = expected_task

        # Act
        result = task_service.get_task(task_id)

        # Assert
        assert result == expected_task
        mock_repository.get_by_id.assert_called_once_with(task_id)

    def test_update_task(self, task_service: TaskService, mock_repository: Mock):
        """
        Tests that the update_task service method correctly calls the
        repository's update method.
        """
        # Arrange
        task_id = 1
        task_update = TaskUpdate(title="Updated Task", completed=True)
        expected_task = Task(id=task_id, title="Updated Task", completed=True)
        mock_repository.update.return_value = expected_task

        # Act
        result = task_service.update_task(task_id, task_update)

        # Assert
        assert result == expected_task
        mock_repository.update.assert_called_once_with(task_id, task_update)

    def test_delete_task(self, task_service: TaskService, mock_repository: Mock):
        """
        Tests that the delete_task service method correctly calls the
        repository's delete method.
        """
        # Arrange
        task_id = 1
        mock_repository.delete.return_value = True

        # Act
        result = task_service.delete_task(task_id)

        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with(task_id)