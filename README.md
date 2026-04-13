# KB Orchestrator API

Backend Python que orquestra um fluxo de busca em base de conhecimento (KB) com resposta gerada por LLM.

## Como executar

1. Clone o repositório:
```bash
git clone https://github.com/felipecezar01/kd-orchestrator-api.git
cd kd-orchestrator-api
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env e preencha LLM_API_KEY com sua chave
```

3. Suba o projeto:
```bash
docker compose up --build
```

4. Acesse o Swagger em http://localhost:8000/docs

## Stack

- Python 3.12
- FastAPI + Uvicorn
- httpx (requisições HTTP assíncronas)
- OpenAI SDK (compatível com Gemini via base_url)
- Docker + Docker Compose

## Estrutura do projeto

```
app/
  main.py           # Endpoint POST /messages, validação com Pydantic
  orchestrator.py    # Orquestra o fluxo: tool -> LLM -> resposta
  tool.py            # Busca contexto na KB via HTTP
  llm_client.py      # Envia pergunta + contexto para o LLM
```

## Fluxo da aplicação

1. O usuário envia uma mensagem via POST /messages
2. O Pydantic valida a entrada (message obrigatório, não pode ser vazio)
3. O orquestrador chama a tool para buscar contexto na KB
4. A tool faz GET na KB_URL, parseia o markdown em seções e retorna trechos relevantes
5. Se encontrou contexto: o orquestrador monta o prompt e chama o LLM, retornando answer + sources
6. Se não encontrou contexto e não tem histórico de sessão: retorna fallback padrão sem chamar o LLM
7. Se não encontrou contexto mas tem histórico de sessão: chama o LLM com o histórico para perguntas de continuidade
8. Após a resposta do LLM, o sistema valida se a saída parece um fallback e padroniza a frase exata do contrato

## Regras de decisão do fluxo

- A tool é chamada sempre que há uma message válida
- A busca filtra seções por match de título com remoção de stop words para evitar falsos positivos
- O contexto retornado entra no LLM apenas se houver trechos relevantes
- Se não houver contexto e não houver histórico, retorna fallback direto sem consumir chamada ao LLM
- Se houver histórico de sessão, o LLM recebe o histórico para responder perguntas de continuidade
- O LLM recebe instrução para responder apenas com base no contexto fornecido
- Após a resposta do LLM, o código valida a saída: se parecer com fallback, padroniza a frase exata e limpa os sources

## Session ID (diferencial)

A API aceita um campo opcional session_id na requisição. Quando presente, o sistema mantém um histórico curto da conversa em memória, permitindo perguntas de continuidade como "pode resumir o que falamos?".

- Sessões são isoladas: cada session_id tem seu próprio histórico
- Histórico limitado a 10 mensagens por sessão (janela curta)
- Armazenamento em memória (dicionário Python): o histórico é perdido se o contêiner reiniciar
- Sem session_id, cada chamada é independente

## Decisões técnicas

- FastAPI: escolhido por gerar Swagger automático, suportar async nativamente, e integrar validação com Pydantic
- httpx em vez de requests: suporta chamadas assíncronas, consistente com o fluxo async do FastAPI
- OpenAI SDK apontando para Gemini: o SDK da OpenAI funciona como cliente HTTP genérico. Configurando base_url para o endpoint do Gemini, o mesmo código funciona com qualquer provider compatível
- Busca por stop words em vez de TF-IDF ou embeddings: a KB tem 14 seções com títulos descritivos e curtos. Para esse escopo, match por título com filtragem de stop words é a abordagem mais pragmática. Para uma KB maior, o próximo passo seria TF-IDF (scikit-learn) ou embeddings com banco vetorial
- Validação de fallback no código: após a resposta do LLM, o orquestrador verifica se o texto parece um fallback e padroniza a frase exata. Isso segue a recomendação do desafio de não confiar em temperature para garantir formato
- Provider configurável: LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL e LLM_API_KEY são variáveis de ambiente. Trocar de Gemini para outro provider compatível não exige mudança no código

## Makefile

```bash
make up     # Sobe o ambiente
make down   # Encerra o ambiente
make test   # Testa o endpoint com pergunta sobre composição
```