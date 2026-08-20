from fastapi import APIRouter, Depends, HTTPException

from ..config import settings
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.ai import AiChatRequest, AiChatResponse, AiHealthResponse
from ..services import ai as ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health", response_model=AiHealthResponse, summary="Check AI service status")
async def ai_health(current_user: User = Depends(get_current_user)):
  available = await ai_service.check_availability() if settings.ai_enabled else False
  return AiHealthResponse(
    enabled=settings.ai_enabled,
    available=available,
    model=settings.ai_model,
  )


@router.post("/chat", response_model=AiChatResponse, summary="Send a message to the AI assistant")
async def ai_chat(
  body: AiChatRequest,
  current_user: User = Depends(get_current_user),
):
  try:
    reply, model = await ai_service.chat(body.message)
    return AiChatResponse(reply=reply, model=model)
  except ai_service.AiDisabledError:
    raise HTTPException(503, detail={"message": "AI is disabled", "field": "ai"})
  except ai_service.AiEmptyMessageError:
    raise HTTPException(400, detail={"message": "Message cannot be empty", "field": "message"})
  except ai_service.AiUnavailableError as exc:
    raise HTTPException(503, detail={"message": str(exc), "field": "ai"})
  except ai_service.AiRequestError as exc:
    raise HTTPException(502, detail={"message": f"AI request failed: {exc}", "field": "ai"})