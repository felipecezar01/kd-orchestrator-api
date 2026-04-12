from app.tool import search_kb
from app.llm_client import ask_llm

FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."

# Memória de sessões em dicionário (morre se o contêiner reiniciar)
sessions: dict[str, list[dict]] = {}

# Máximo de mensagens por sessão (janela curta)
MAX_HISTORY = 10


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

    # 1. Recupera histórico da sessão, se existir
    history = []
    if session_id and session_id in sessions:
        history = sessions[session_id]

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
            sessions[session_id] = []
        sessions[session_id].append({"role": "user", "content": message})
        sessions[session_id].append({"role": "assistant", "content": answer})
        sessions[session_id] = sessions[session_id][-MAX_HISTORY:]

    return {"answer": answer, "sources": sources}