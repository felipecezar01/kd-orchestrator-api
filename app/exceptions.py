class KBError(Exception):
    """Erro ao acessar ou processar a base de conhecimento."""
    pass


class LLMError(Exception):
    """Erro ao chamar o provider LLM."""
    pass