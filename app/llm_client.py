from openai import AsyncOpenAI


async def ask_llm(
    question: str,
    context: str,
    provider: str,
    model: str,
    api_key: str,
    base_url: str,
    history: list[dict] = None,
) -> str:
    """Envia pergunta + contexto da KB para o LLM e retorna a resposta."""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    if context:
        system_prompt = (
            "Você é um assistente técnico. Responda a pergunta do usuário "
            "usando APENAS o contexto fornecido abaixo. "
            "Se o contexto não for suficiente, responda exatamente: "
            "'Não encontrei informação suficiente na base para responder essa pergunta.'\n\n"
            f"Contexto:\n{context}"
        )
    else:
        system_prompt = (
            "Você é um assistente técnico. O usuário está continuando uma conversa anterior. "
            "Responda com base no histórico da conversa. "
            "Se não houver informação suficiente no histórico, responda exatamente: "
            "'Não encontrei informação suficiente na base para responder essa pergunta.'"
        )

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": question})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content