from app.tool import search_kb
from app.llm_client import ask_llm

FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."


async def handle_message(
    message: str,
    kb_url: str,
    provider: str,
    model: str,
    api_key: str,
    base_url: str,
) -> dict:
    """Orquestra o fluxo: tool -> LLM -> resposta."""

    # 1. Chama a tool pra buscar contexto na KB
    results = await search_kb(message, kb_url)

    # 2. Sem contexto? Fallback direto, sem chamar LLM
    if not results:
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # 3. Monta o contexto juntando os trechos encontrados
    context = "\n\n".join(
        f"[{r['section']}]\n{r['content']}" for r in results
    )
    sources = [{"section": r["section"]} for r in results]

    # 4. Chama o LLM com pergunta + contexto
    answer = await ask_llm(
        question=message,
        context=context,
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

    return {"answer": answer, "sources": sources}