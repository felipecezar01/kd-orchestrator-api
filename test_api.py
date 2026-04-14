"""Testes manuais da API - funciona em qualquer OS (Linux, macOS, Windows)."""

import json
import urllib.request

BASE_URL = "http://localhost:8000/messages"


def post(message: str, session_id: str = None) -> dict:
    """Envia POST para o endpoint e retorna o JSON de resposta."""
    body = {"message": message}
    if session_id:
        body["session_id"] = session_id

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"status": resp.status, "body": result}
    except urllib.error.HTTPError as e:
        result = json.loads(e.read().decode("utf-8"))
        return {"status": e.code, "body": result}
    except urllib.error.URLError:
        return {"status": None, "body": "Erro de conexão. A API está rodando?"}


def run_test(label: str, message: str, session_id: str = None):
    """Executa um teste e exibe o resultado formatado."""
    print(f"=== {label} ===")
    result = post(message, session_id)
    print(json.dumps(result["body"], indent=2, ensure_ascii=False))
    print()


if __name__ == "__main__":
    run_test("Teste 1: O que é composição?",
             "O que é composição?", "validacao")

    run_test("Teste 2: Qual o papel da Tool de conhecimento?",
             "Qual o papel da Tool de conhecimento?", "validacao")

    run_test("Teste 3: A tool deve responder diretamente ao usuário?",
             "A tool deve responder diretamente ao usuário?", "validacao")

    run_test("Teste 4: Pode resumir em uma frase? (histórico)",
             "Pode resumir em uma frase?", "validacao")

    run_test("Teste 5: Como agir sem contexto suficiente?",
             "Como agir sem contexto suficiente?", "validacao")

    run_test("Teste 6: Quando usar herança?",
             "Quando usar herança?", "validacao")

    run_test("Teste 7: Qual o papel da orquestração?",
             "Qual o papel da orquestração?", "validacao")

    run_test("Teste 8: Onde colocar regra de negócio?",
             "Onde colocar regra de negócio, no endpoint ou no fluxo interno?", "validacao")

    run_test("Teste 9: Pode resumir o que falamos? (histórico completo)",
             "Pode resumir o que falamos?", "validacao")

    run_test("Teste 10: Isolamento de sessão (outra-sessao)",
             "Pode resumir o que falamos?", "outra-sessao")

    print("=== Todos os testes finalizados ===")