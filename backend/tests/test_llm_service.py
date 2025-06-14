"""Tests for the LLMService."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.llm_service import LLMService
from app.schemas.task import TaskCreate

# A dictionary to simulate LLM responses for consistency in tests.
MOCK_LLM_RESPONSES = {
    "taxes": '{"title": "Submit taxes", "due_date": "2024-01-15T12:00:00", "priority": "high"}'
}

class TestLLMService:
    """A suite of tests for the LLMService class."""

    @pytest.fixture
    def llm_service_no_client(self) -> LLMService:
        """
        Pytest fixture to create an instance of LLMService without an API client.
        This simulates the scenario where no API key is provided.
        """
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = None
            yield LLMService()

    @pytest.fixture
    def llm_service_with_client(self) -> LLMService:
        """
        Pytest fixture to create an instance of LLMService with a mocked API client.
        This allows for testing the LLM interaction logic without making real API calls.
        """
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = "fake-api-key"
            with patch('app.services.llm_service.Anthropic') as mock_anthropic:
                service = LLMService()
                # Replace the real client with a mock object.
                service.client = Mock()
                yield service

    # --- Tests for the Fallback Parser ---

    def test_fallback_parser_simple_title(self, llm_service_no_client: LLMService):
        """Tests that the fallback parser correctly extracts a simple title."""
        result = llm_service_no_client._fallback_parser("Call mom")
        assert isinstance(result, TaskCreate)
        assert result.title == "Call mom"
        assert result.description is None
        assert result.due_date is None
        assert result.priority is None

    def test_fallback_parser_extracts_time(self, llm_service_no_client: LLMService):
        """Tests that the fallback parser correctly identifies and extracts a time expression."""
        result = llm_service_no_client._fallback_parser("Buy groceries tomorrow")
        assert result.title == "Buy groceries"
        assert result.due_date is not None
        assert result.due_date.date() == (datetime.now() + timedelta(days=1)).date()

    def test_fallback_parser_extracts_priority(self, llm_service_no_client: LLMService):
        """Tests that the fallback parser correctly identifies and extracts a priority level."""
        result = llm_service_no_client._fallback_parser("Submit report high priority")
        assert result.title == "Submit report"
        assert result.priority == "high"

    def test_fallback_parser_extracts_specific_time(self, llm_service_no_client: LLMService):
        """Tests the fallback parser's ability to extract a specific time of day."""
        result = llm_service_no_client._fallback_parser("Meeting tomorrow at 3pm")
        assert result.title == "Meeting"
        assert result.due_date is not None
        assert result.due_date.hour == 15
        assert result.due_date.minute == 0

    def test_fallback_parser_cleans_prefix(self, llm_service_no_client: LLMService):
        """Tests that the fallback parser correctly removes common conversational prefixes."""
        result = llm_service_no_client._fallback_parser("Remind me to submit taxes")
        assert result.title == "submit taxes"

    # --- Tests for LLM Interaction and Fallback Logic ---

    def test_parse_with_llm_successful_call(self, llm_service_with_client: LLMService):
        """
        Tests a successful LLM parsing scenario where the API returns a valid JSON response.
        """
        # Arrange: Set up the mock client to return a predictable response.
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=MOCK_LLM_RESPONSES["taxes"])]
        llm_service_with_client.client.messages.create.return_value = mock_response

        # Act: Call the method that interacts with the LLM.
        result = llm_service_with_client._parse_with_llm("remind me to submit taxes next Monday at noon")

        # Assert: Verify the output and that the mock client was called.
        assert isinstance(result, TaskCreate)
        assert result.title == "Submit taxes"
        assert result.priority == "high"
        assert result.due_date is not None
        llm_service_with_client.client.messages.create.assert_called_once()

    def test_main_parse_function_falls_back_on_llm_error(self, llm_service_with_client: LLMService):
        """
        Tests that the main parsing function correctly falls back to the rule-based
        parser when the LLM client throws an exception.
        """
        # Arrange: Configure the mock client to raise an error when called.
        llm_service_with_client.client.messages.create.side_effect = Exception("API Communication Error")

        # Act: Patch the fallback parser to monitor if it gets called, then run the main function.
        with patch.object(llm_service_with_client, '_fallback_parser', wraps=llm_service_with_client._fallback_parser) as mock_fallback:
            result = llm_service_with_client.parse_natural_language("some text that will fail")

        # Assert: Check that the fallback was called and returned a result.
        mock_fallback.assert_called_once_with("some text that will fail")
        assert result.title == "some text that will fail" # As per basic fallback logic

    def test_main_parse_function_uses_fallback_when_no_client(self, llm_service_no_client: LLMService):
        """
        Tests that the main parsing function uses the fallback parser from the start
        if the LLM client was never initialized.
        """
        # Act: Patch the fallback parser and call the main function.
        with patch.object(llm_service_no_client, '_fallback_parser', wraps=llm_service_no_client._fallback_parser) as mock_fallback:
            result = llm_service_no_client.parse_natural_language("a simple task")

        # Assert: Verify that the fallback was used.
        mock_fallback.assert_called_once_with("a simple task")
        assert result.title == "a simple task"