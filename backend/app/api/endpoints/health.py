"""
Health check endpoint for the application.

This module provides a simple health check endpoint to verify the operational
status of the application and its key dependencies, such as the LLM service.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.llm_service import LLMService

router = APIRouter()


class HealthStatus(BaseModel):
    """Pydantic schema for the health check response."""
    status: str
    llm_service: str


@router.get("/health", response_model=HealthStatus, tags=["Health"])
def health_check(llm_service: LLMService = Depends(LLMService)):
    """
    Check the health of the application.
    
    This endpoint provides a simple way to monitor the application's status.
    It returns a JSON object indicating if the service is running and also
    reports the current status of the LLM service connection.
    """
    llm_status = "available" if llm_service.client else "unavailable (using fallback)"
    return HealthStatus(status="ok", llm_service=llm_status) 