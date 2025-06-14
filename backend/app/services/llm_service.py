"""
LLM service for natural language processing.

This module provides a service for parsing natural language text into structured
task data. It features a primary LLM-based parser and a robust, rule-based
fallback parser to ensure functionality even when the LLM is unavailable.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dateutil import parser
import re

from anthropic import Anthropic
from app.config import settings
from app.schemas.task import TaskCreate

logger = logging.getLogger(__name__)

class LLMService:
    """
    A service class for handling all LLM-based natural language processing.
    It initializes the Anthropic client and orchestrates the parsing process,
    including the fallback mechanism.
    """
    
    def __init__(self):
        """
        Initializes the LLMService.
        
        If an Anthropic API key is provided in the settings, it attempts to
        initialize the client. Otherwise, it logs a warning and prepares to
        use the fallback parser exclusively.
        """
        self.client = None
        if settings.anthropic_api_key:
            try:
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
        else:
            logger.warning("No Anthropic API key provided, will use rule-based fallback parser.")
    
    def parse_natural_language(self, text: str) -> TaskCreate:
        """
        Parses natural language text into a structured TaskCreate schema.
        
        This method attempts to use the LLM for parsing first. If the LLM client
        is not available or if the LLM call fails, it gracefully falls back
        to a rule-based parser.
        
        Args:
            text: The raw natural language string from the user.
            
        Returns:
            A TaskCreate schema object populated with the parsed data.
        """
        logger.info(f"Parsing natural language input: '{text}'")
        
        if self.client:
            try:
                return self._parse_with_llm(text)
            except Exception as e:
                logger.error(f"LLM parsing failed: {e}, falling back to rule-based parser.")
                return self._fallback_parser(text)
        else:
            logger.info("LLM client not available, using rule-based fallback parser.")
            return self._fallback_parser(text)
    
    def _parse_with_llm(self, text: str) -> TaskCreate:
        """
        Parses the text using the configured LLM (Anthropic Claude).
        
        This method constructs a detailed prompt with instructions, examples,
        and a safety guardrail to guide the LLM's response.
        
        Args:
            text: The user's natural language input.
            
        Returns:
            A TaskCreate schema object from the LLM's output.
            
        Raises:
            Exception: If the LLM call or JSON parsing fails for unexpected reasons.
        """
        try:
            logger.debug(f"Attempting to parse with LLM: '{text}'")
            
            # This prompt is engineered with a specific safety instruction.
            # If the input is inappropriate, the LLM is instructed to return a
            # pre-defined, sanitized JSON object instead of the user's harmful text.
            sanitized_title = "Inappropriate Content"
            sanitized_description = "Original request was flagged as inappropriate and has been sanitized."
            
            prompt = f"""You are a helpful assistant that converts natural language text into a structured task in JSON format.

--- TASK STRUCTURE ---
You must always return a single, valid JSON object with this structure:
{{
    "title": "concise task title",
    "description": "additional details if any (optional)",
    "due_date": "ISO format datetime if mentioned (optional)",
    "priority": "high/medium/low if mentioned (optional)"
}}

--- SAFETY GUARDRAIL ---
If the user's text is abusive, illegal, inappropriate, promotes self-harm, or is otherwise unethical, you MUST NOT use the user's text. Instead, you MUST respond with EXACTLY this JSON object:
{{
    "title": "{sanitized_title}",
    "description": "{sanitized_description}",
    "due_date": "{(datetime.now() + timedelta(hours=1)).isoformat()}"
}}

--- EXAMPLES ---
User text: "remind me to submit taxes next Monday at noon"
Your response: {{"title": "Submit taxes", "due_date": "2024-XX-XXT12:00:00"}}

User text: "an abusive or inappropriate request"
Your response: {{"title": "{sanitized_title}", "description": "{sanitized_description}", "due_date": "{(datetime.now() + timedelta(hours=1)).isoformat()}"}}

--- CURRENT CONTEXT ---
Current date/time for reference: {datetime.now().isoformat()}

--- USER REQUEST ---
User text: "{text}"
Your response:"""
            
            response = self.client.messages.create(
                model=settings.model,
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }],
                max_tokens=500,
                temperature=0.3
            )
            
            logger.debug(f"LLM response: {response.content[0].text}")
            
            # Extract JSON from response
            json_str = response.content[0].text.strip()
            # The LLM might wrap the JSON in a markdown code block, so we use a regex
            # to reliably extract the JSON content.
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            
            parsed_data = json.loads(json_str)
            logger.info(f"Successfully parsed data from LLM: {parsed_data}")
            
            # The LLM returns dates as strings, so we need to parse them into
            # datetime objects for our schema.
            if parsed_data.get("due_date"):
                try:
                    parsed_data["due_date"] = parser.parse(parsed_data["due_date"])
                except (parser.ParserError, TypeError) as e:
                    logger.warning(f"LLM returned a due_date that could not be parsed: '{parsed_data['due_date']}'. Error: {e}")
                    parsed_data["due_date"] = None
            
            return TaskCreate(**parsed_data)
            
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM parsing: {e}")
            raise
    
    def _fallback_parser(self, text: str) -> TaskCreate:
        """
        A rule-based fallback parser for when the LLM is unavailable.
        
        This parser uses regular expressions to extract priority, dates, and times
        from the text. It provides a baseline level of "smart" parsing and ensures
        the feature remains functional without an LLM.

        Justification: Guarantees core functionality ("Natural-language -> Task")
        is always available, even without an API key or during an API outage. This
        improves resilience and the developer experience.
        
        Trade-off: This parser is rigid. It can only handle patterns it's been
        explicitly programmed to recognize and is less "intelligent" than the LLM.
        Adding more complex patterns increases its maintenance overhead.

        Args:
            text: The user's natural language input.
            
        Returns:
            A TaskCreate schema object populated with the parsed data.
        """
        logger.debug(f"Using rule-based fallback parser for: '{text}'")
        
        # Start with the full text as the title, to be refined later.
        result = {
            "title": text,
            "description": None,
            "due_date": None,
            "priority": None
        }
        
        # --- Priority Extraction ---
        # Look for keywords indicating priority and remove them from the text.
        priority_patterns = {
            "high": r'\b(high|urgent|important|critical)\s*priority\b',
            "medium": r'\b(medium|normal)\s*priority\b',
            "low": r'\b(low|minor)\s*priority\b'
        }
        
        for priority, pattern in priority_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                result["priority"] = priority
                text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                break
        
        # --- Date & Time Extraction ---
        # A list of regex patterns to find relative and absolute date expressions.
        # The list is ordered to avoid conflicts (e.g., "next monday" vs "monday").
        time_patterns = [
            (r'\b(today)\b', lambda m: datetime.now().replace(hour=23, minute=59, second=59)),
            (r'\b(tomorrow)\b', lambda m: datetime.now() + timedelta(days=1)),
            (r'\b(next monday)\b', lambda m: self._next_weekday(0)),
            (r'\b(next tuesday)\b', lambda m: self._next_weekday(1)),
            (r'\b(next wednesday)\b', lambda m: self._next_weekday(2)),
            (r'\b(next thursday)\b', lambda m: self._next_weekday(3)),
            (r'\b(next friday)\b', lambda m: self._next_weekday(4)),
            (r'\b(next saturday)\b', lambda m: self._next_weekday(5)),
            (r'\b(next sunday)\b', lambda m: self._next_weekday(6)),
            (r'\b(next week)\b', lambda m: datetime.now() + timedelta(weeks=1)),
            (r'\bin (\d+) days?\b', lambda m: datetime.now() + timedelta(days=int(m.group(1)))),
            (r'\bin (\d+) hours?\b', lambda m: datetime.now() + timedelta(hours=int(m.group(1)))),
        ]
        
        for pattern, date_func in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result["due_date"] = date_func(match)
                    # Remove the matched date expression from the text to clean up the title.
                    text = text[:match.start()] + text[match.end():].strip()
                    break
                except Exception as e:
                    logger.warning(f"Failed to parse date from pattern '{pattern}': {e}")
        
        # --- Time of Day Extraction ---
        # If a date was found, look for a specific time of day.
        time_match = re.search(r'\b(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|noon|midnight)\b', text, re.IGNORECASE)
        if time_match and result["due_date"]:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            period = time_match.group(3).lower()
            
            if period == "noon":
                hour, minute = 12, 0
            elif period == "midnight":
                hour, minute = 0, 0
            elif period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            
            result["due_date"] = result["due_date"].replace(hour=hour, minute=minute, second=0, microsecond=0)
            text = text[:time_match.start()] + text[time_match.end():]
        
        # --- Title Cleanup ---
        # Remove any leftover whitespace and common conversational prefixes.
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^(remind me to|remember to|don\'t forget to)\s+', '', text, flags=re.IGNORECASE)
        
        # Assign the cleaned-up text as the final title. Default if empty.
        result["title"] = text or "New Task"
        
        logger.info(f"Fallback parser produced result: {result}")
        return TaskCreate(**result)
    
    def _next_weekday(self, weekday: int) -> datetime:
        """
        Calculates the date of the next occurrence of a given weekday.
        
        Args:
            weekday: The target weekday, where Monday is 0 and Sunday is 6.
            
        Returns:
            A datetime object representing the next occurrence of that day.
        """
        today = datetime.now()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days=days_ahead)