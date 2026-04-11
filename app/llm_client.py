from openai import AsyncOpenAI


async def ask_llm(
    question: str,
    context: str,
    provider: str,
    model: str,
    api_key: str,
    base_url: str,
) -> str:
    """Envia pergunta + contexto da KB para o LLM e retorna a resposta."""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    system_prompt = (
        "Você é um assistente técnico. Responda a pergunta do usuário "
        "usando APENAS o contexto fornecido abaixo. "
        "Se o contexto não for suficiente, responda exatamente: "
        "'Não encontrei informação suficiente na base para responder essa pergunta.'\n\n"
        f"Contexto:\n{context}"
    )

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content