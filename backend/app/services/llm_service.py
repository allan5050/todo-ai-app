"""LLM service for natural language processing."""
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
    """Service for LLM-based natural language processing."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.client = None
        if settings.anthropic_api_key:
            try:
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
        else:
            logger.warning("No Anthropic API key provided, using fallback parser")
    
    def parse_natural_language(self, text: str) -> TaskCreate:
        """Parse natural language text into a task."""
        logger.info(f"Parsing natural language: {text}")
        
        if self.client:
            try:
                return self._parse_with_llm(text)
            except Exception as e:
                logger.error(f"LLM parsing failed: {str(e)}, falling back to rule-based parser")
                return self._fallback_parser(text)
        else:
            logger.debug("No LLM client available, using fallback parser")
            return self._fallback_parser(text)
    
    def _parse_with_llm(self, text: str) -> TaskCreate:
        """Parse text using LLM."""
        try:
            logger.debug(f"Sending request to LLM for text: {text}")
            
            prompt = f"""Parse the following natural language task description into structured data.
Extract the task title, description (if any), due date/time (if mentioned), and priority (if mentioned).

Text: "{text}"

Return ONLY a JSON object with this structure:
{{
    "title": "concise task title",
    "description": "additional details if any (optional)",
    "due_date": "ISO format datetime if mentioned (optional)",
    "priority": "high/medium/low if mentioned (optional)"
}}

Current date/time for reference: {datetime.now().isoformat()}

Examples:
- "remind me to submit taxes next Monday at noon" -> {{"title": "Submit taxes", "due_date": "2024-XX-XX 12:00:00"}}
- "buy groceries tomorrow high priority" -> {{"title": "Buy groceries", "due_date": "2024-XX-XX", "priority": "high"}}
- "call mom" -> {{"title": "Call mom"}}"""
            
            response = self.client.messages.create(
                model=os.getenv('MODEL'),
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
            # Try to extract JSON if it's wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            
            parsed_data = json.loads(json_str)
            logger.debug(f"Parsed data: {parsed_data}")
            
            # Convert due_date string to datetime if present
            if parsed_data.get("due_date"):
                try:
                    parsed_data["due_date"] = parser.parse(parsed_data["due_date"])
                except Exception as e:
                    logger.warning(f"Failed to parse due_date: {e}")
                    parsed_data["due_date"] = None
            
            return TaskCreate(**parsed_data)
            
        except Exception as e:
            logger.error(f"Error in LLM parsing: {str(e)}")
            raise
    
    def _fallback_parser(self, text: str) -> TaskCreate:
        """Fallback rule-based parser for when LLM is unavailable."""
        logger.debug(f"Using fallback parser for: {text}")
        
        # Initialize result
        result = {
            "title": text,
            "description": None,
            "due_date": None,
            "priority": None
        }
        
        # Extract priority
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
        
        # Extract time expressions
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
                    text = text[:match.start()] + text[match.end():].strip()
                    break
                except Exception as e:
                    logger.warning(f"Failed to parse date pattern: {e}")
        
        # Extract time of day
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
            
            result["due_date"] = result["due_date"].replace(hour=hour, minute=minute)
            text = text[:time_match.start()] + text[time_match.end():]
        
        # Clean up title
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^(remind me to|remember to|don\'t forget to)\s+', '', text, flags=re.IGNORECASE)
        
        result["title"] = text or "New Task"
        
        logger.debug(f"Fallback parser result: {result}")
        return TaskCreate(**result)
    
    def _next_weekday(self, weekday: int) -> datetime:
        """Get the next occurrence of a weekday (0=Monday, 6=Sunday)."""
        today = datetime.now()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days=days_ahead)