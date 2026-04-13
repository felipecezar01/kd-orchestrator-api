import time
from app.tool import search_kb
from app.llm_client import ask_llm

FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."

# Memória de sessões em dicionário (morre se o contêiner reiniciar)
sessions: dict[str, dict] = {}

# Máximo de mensagens por sessão (janela curta)
MAX_HISTORY = 10

# Tempo de expiração da sessão em segundos (30 minutos)
SESSION_TTL = 1800


def cleanup_expired_sessions():
    """Remove sessões que passaram do TTL."""
    now = time.time()
    expired = [sid for sid, data in sessions.items() if now - data["last_access"] > SESSION_TTL]
    for sid in expired:
        del sessions[sid]


async def handle_message(
    message: str,
    kb_url: str,
    provider: str,
    model: str,
    api_key: str,
    base_url: str,
    session_id: str = None,
) -> dict:
    """Orquestra o fluxo: tool -> LLM -> resposta."""

    # 0. Limpa sessões expiradas
    cleanup_expired_sessions()

    # 1. Recupera histórico da sessão, se existir
    history = []
    if session_id and session_id in sessions:
        history = sessions[session_id]["history"]

    # 2. Chama a tool pra buscar contexto na KB
    results = await search_kb(message, kb_url)

    # 3. Sem contexto E sem histórico? Fallback direto, sem chamar LLM
    if not results and not history:
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # 4. Monta o contexto juntando os trechos encontrados
    context = ""
    sources = []
    if results:
        context = "\n\n".join(
            f"[{r['section']}]\n{r['content']}" for r in results
        )
        sources = [{"section": r["section"]} for r in results]

    # 5. Chama o LLM com pergunta + contexto + histórico
    answer = await ask_llm(
        question=message,
        context=context,
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        history=history,
    )

    # 6. Se o LLM retornou algo parecido com fallback, padroniza a frase exata
    if "não encontrei" in answer.lower() and "suficiente" in answer.lower():
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # 7. Salva no histórico da sessão, se tiver session_id
    if session_id:
        if session_id not in sessions:
            sessions[session_id] = {"history": [], "last_access": time.time()}
        sessions[session_id]["history"].append({"role": "user", "content": message})
        sessions[session_id]["history"].append({"role": "assistant", "content": answer})
        sessions[session_id]["history"] = sessions[session_id]["history"][-MAX_HISTORY:]
        sessions[session_id]["last_access"] = time.time()

    return {"answer": answer, "sources": sources}