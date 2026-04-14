import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from app.orchestrator import handle_message
from app.exceptions import KBError, LLMError

logger = logging.getLogger(__name__)

app = FastAPI(title="KB Orchestrator API")

REQUIRED_ENV_VARS = ["KB_URL", "LLM_PROVIDER", "LLM_MODEL", "LLM_API_KEY", "LLM_BASE_URL"]


@app.on_event("startup")
def validate_env():
    """Valida variáveis de ambiente obrigatórias no startup."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Variáveis de ambiente obrigatórias faltando: {', '.join(missing)}")


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
    except KBError as e:
        logger.error(f"Erro na KB: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Erro ao acessar a base de conhecimento.")
    except LLMError as e:
        logger.error(f"Erro no LLM: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Erro ao consultar o modelo de linguagem.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")