import os
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from app.orchestrator import handle_message

app = FastAPI(title="KB Orchestrator API")


class MessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


class Source(BaseModel):
    section: str


class MessageResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/messages", response_model=MessageResponse)
async def post_message(request: MessageRequest):
    """Recebe uma pergunta e retorna resposta baseada na KB."""
    result = await handle_message(
        message=request.message,
        kb_url=os.getenv("KB_URL"),
        provider=os.getenv("LLM_PROVIDER"),
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )
    return result