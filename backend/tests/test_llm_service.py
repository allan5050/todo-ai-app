"""Tests for LLM service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.llm_service import LLMService
from app.schemas.task import TaskCreate


class TestLLMService:
    """Test cases for LLMService."""
    
    @pytest.fixture
    def llm_service_no_client(self):
        """Create LLM service without API client."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = None
            return LLMService()
    
    @pytest.fixture
    def llm_service_with_client(self):
        """Create LLM service with mocked API client."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            with patch('app.services.llm_service.Anthropic') as mock_anthropic:
                service = LLMService()
                service.client = Mock()
                return service
    
    def test_fallback_parser_simple(self, llm_service_no_client):
        """Test fallback parser with simple text."""
        # Act
        result = llm_service_no_client._fallback_parser("Call mom")
        
        # Assert
        assert isinstance(result, TaskCreate)
        assert result.title == "Call mom"
        assert result.description is None
        assert result.due_date is None
        assert result.priority is None
    
    def test_fallback_parser_with_time(self, llm_service_no_client):
        """Test fallback parser with time expressions."""
        # Act
        result = llm_service_no_client._fallback_parser("Buy groceries tomorrow")
        
        # Assert
        assert isinstance(result, TaskCreate)
        assert result.title == "Buy groceries"
        assert result.due_date is not None
        assert result.due_date.date() == (datetime.now() + timedelta(days=1)).date()
    
    def test_fallback_parser_with_priority(self, llm_service_no_client):
        """Test fallback parser with priority."""
        # Act
        result = llm_service_no_client._fallback_parser("Submit report high priority")
        
        # Assert
        assert isinstance(result, TaskCreate)
        assert result.title == "Submit report"
        assert result.priority == "high"
    
    def test_fallback_parser_with_time_and_hour(self, llm_service_no_client):
        """Test fallback parser with specific time."""
        # Act
        result = llm_service_no_client._fallback_parser("Meeting tomorrow at 3pm")
        
        # Assert
        assert isinstance(result, TaskCreate)
        assert result.title == "Meeting"
        assert result.due_date is not None
        assert result.due_date.hour == 15
        assert result.due_date.minute == 0
    
    def test_fallback_parser_remind_me_to(self, llm_service_no_client):
        """Test fallback parser removes 'remind me to' prefix."""
        # Act
        result = llm_service_no_client._fallback_parser("Remind me to submit taxes")
        
        # Assert
        assert result.title == "submit taxes"
    
    def test_parse_with_llm_success(self, llm_service_with_client):
        """Test successful LLM parsing."""
        # Arrange
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"title": "Submit taxes", "due_date": "2024-01-15T12:00:00"}')]
        llm_service_with_client.client.messages.create.return_value = mock_response
        
        # Act
        result = llm_service_with_client._parse_with_llm("remind me to submit taxes next Monday at noon")
        
        # Assert
        assert isinstance(result, TaskCreate)
        assert result.title == "Submit taxes"
        assert result.due_date is not None
        llm_service_with_client.client.messages.create.assert_called_once()
    
    def test_parse_with_llm_fallback_on_error(self, llm_service_with_client):
        """Test LLM parsing falls back on error."""
        # Arrange
        llm_service_with_client.client.messages.create.side_effect = Exception("API Error")
        
        # Act
        with patch.object(llm_service_with_client, '_fallback_parser') as mock_fallback:
            mock_fallback.return_value = TaskCreate(title="Fallback task")
            result = llm_service_with_client.parse_natural_language("test text")
        
        # Assert
        mock_fallback.assert_called_once_with("test text")
        assert result.title == "Fallback task"
    
    def test_parse_natural_language_no_client(self, llm_service_no_client):
        """Test parsing without LLM client uses fallback."""
        # Act
        with patch.object(llm_service_no_client, '_fallback_parser') as mock_fallback:
            mock_fallback.return_value = TaskCreate(title="Fallback task")
            result = llm_service_no_client.parse_natural_language("test text")
        
        # Assert
        mock_fallback.assert_called_once_with("test text")
        assert result.title == "Fallback task"