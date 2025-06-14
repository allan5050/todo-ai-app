"""Health check endpoint."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.llm_service import LLMService

router = APIRouter()


class HealthStatus(BaseModel):
    status: str
    llm_service: str


@router.get("/health", response_model=HealthStatus, tags=["Health"])
def health_check(llm_service: LLMService = Depends()):
    """
    Check the health of the application.
    
    Reports the overall status and the availability of the LLM service.
    """
    return {
        "status": "ok",
        "llm_service": "available" if llm_service.client else "unavailable (using fallback)"
    } 