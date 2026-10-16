
import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.claim import get_current_user
from langgraph_agent import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    try:
        reply = await run_agent(
            message=request.message,
            history=[
                item.model_dump()
                for item in request.history
            ],
        )
        return ChatResponse(reply=reply)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "AI chat failed for authenticated user %s",
            user.get("username", "unknown"),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI assistant could not process this request. Please try again.",
        ) from None
