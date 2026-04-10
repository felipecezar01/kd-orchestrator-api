import httpx


async def fetch_kb(kb_url: str) -> str:
    """Faz GET na URL da KB e retorna o texto markdown."""
    async with httpx.AsyncClient() as client:
        response = await client.get(kb_url)
        response.raise_for_status()
        return response.text


def parse_sections(markdown: str) -> dict[str, str]:
    """Quebra o markdown em seções. Cada '## Titulo' vira uma chave."""
    sections = {}
    current_title = None
    current_content = []

    for line in markdown.split("\n"):
        if line.startswith("## "):
            if current_title:
                sections[current_title] = "\n".join(current_content).strip()
            current_title = line.replace("## ", "").strip()
            current_content = []
        elif current_title:
            current_content.append(line)

    if current_title:
        sections[current_title] = "\n".join(current_content).strip()

    return sections


def search_sections(question: str, sections: dict[str, str]) -> list[dict]:
    """Busca seções relevantes comparando palavras da pergunta com o conteúdo."""
    question_lower = question.lower()
    results = []

    for title, content in sections.items():
        title_lower = title.lower()
        content_lower = content.lower()

        if title_lower in question_lower or question_lower in title_lower:
            results.append({"section": title, "content": content})
            continue

        question_words = set(question_lower.split())
        section_words = set(title_lower.split()) | set(content_lower.split())

        common = question_words & section_words
        if len(common) >= 2:
            results.append({"section": title, "content": content})

    return results


async def search_kb(question: str, kb_url: str) -> list[dict]:
    """Função principal: baixa a KB, parseia e busca trechos relevantes."""
    markdown = await fetch_kb(kb_url)
    sections = parse_sections(markdown)
    return search_sections(question, sections)