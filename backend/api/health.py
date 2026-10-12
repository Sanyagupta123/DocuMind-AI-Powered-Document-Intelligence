from fastapi import APIRouter

from backend.config import settings
from backend.schemas.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.app_env}
