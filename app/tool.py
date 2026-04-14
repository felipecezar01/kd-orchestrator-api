import time
import httpx
from app.exceptions import KBError

# Cache da KB em memória (compartilhado entre todas as requests)
_kb_cache: str | None = None
_kb_cache_time: float = 0.0
KB_CACHE_TTL = 300  # 5 minutos


async def fetch_kb(kb_url: str) -> str:
    """Faz GET na URL da KB e retorna o texto markdown. Usa cache se disponível."""
    global _kb_cache, _kb_cache_time

    if _kb_cache and (time.time() - _kb_cache_time) < KB_CACHE_TTL:
        return _kb_cache

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(kb_url)
            response.raise_for_status()
            _kb_cache = response.text
            _kb_cache_time = time.time()
            return _kb_cache
    except httpx.TimeoutException:
        raise KBError("Timeout ao acessar a KB. Verifique a URL e a conexão.")
    except httpx.HTTPStatusError as e:
        raise KBError(f"Erro HTTP ao acessar a KB: {e.response.status_code}")
    except httpx.RequestError as e:
        raise KBError(f"Erro de conexão ao acessar a KB: {str(e)}")


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
    stop_words = {
        "o", "a", "os", "as", "de", "do", "da", "dos", "das", "que",
        "é", "e", "em", "um", "uma", "para", "com", "no", "na", "se",
        "por", "como", "qual", "ao", "ou", "ser", "ter", "não", "mais",
        "quando", "deve", "pode", "sobre", "isso", "esta", "este",
        "the", "is", "what", "how", "and", "of", "in", "to", "a",
        "fluxo", "interno", "onde", "colocar"
    }

    question_words = set(question_lower.split()) - stop_words

    for title, content in sections.items():
        title_lower = title.lower()

        # Match direto: titulo aparece na pergunta
        if title_lower in question_lower:
            results.append({"section": title, "content": content})
            continue

        # Match por palavras relevantes no titulo
        title_words = set(title_lower.split()) - stop_words
        if question_words & title_words:
            results.append({"section": title, "content": content})

    return results


async def search_kb(question: str, kb_url: str) -> list[dict]:
    """Função principal: baixa a KB, parseia e busca trechos relevantes."""
    markdown = await fetch_kb(kb_url)
    sections = parse_sections(markdown)
    return search_sections(question, sections)