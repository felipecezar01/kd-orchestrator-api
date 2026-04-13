import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from app.orchestrator import handle_message

app = FastAPI(title="KB Orchestrator API")


class MessageRequest(BaseModel):
    model_config = {"extra": "forbid"}

    message: str
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > 1000:
            raise ValueError("message cannot exceed 1000 characters")
        return v


class Source(BaseModel):
    section: str


class MessageResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/messages", response_model=MessageResponse)
async def post_message(request: MessageRequest):
    """Recebe uma pergunta e retorna resposta baseada na KB."""
    try:
        result = await handle_message(
            message=request.message,
            kb_url=os.getenv("KB_URL"),
            provider=os.getenv("LLM_PROVIDER"),
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            session_id=request.session_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))