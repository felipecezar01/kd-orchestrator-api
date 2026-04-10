# KB Orchestrator API

Backend Python que orquestra um fluxo de busca em base de conhecimento (KB) com resposta gerada por LLM.

## Como executar

1. Clone o repositório:
```bash
git clone [https://github.com/felipecezar01/kd-orchestrator-api.git](https://github.com/felipecezar01/kd-orchestrator-api.git)
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
```text
app/
├── main.py           # Endpoint POST /messages, validação com Pydantic
├── orchestrator.py   # Orquestra o fluxo: tool -> LLM -> resposta
├── tool.py           # Busca contexto na KB via HTTP
└── llm_client.py     # Envia pergunta + contexto para o LLM
```

## Fluxo da aplicação
1. O usuário envia uma mensagem via `POST /messages`
2. O orquestrador chama a tool para buscar contexto na KB
3. A tool faz `GET` na `KB_URL`, parseia o markdown em seções e retorna trechos relevantes
4. Se encontrou contexto: o orquestrador monta o prompt e chama o LLM, retornando `answer` + `sources`
5. Se não encontrou: retorna fallback padrão sem chamar o LLM

## Regras de decisão do fluxo
- A tool é chamada sempre que há uma `message` válida.
- A busca filtra seções por match de título, ignorando stop words para evitar falsos positivos.
- O contexto retornado entra no LLM apenas se houver trechos relevantes.
- Se não houver contexto, retorna fallback direto sem consumir chamada ao LLM.
- O LLM recebe instrução para responder apenas com base no contexto fornecido.

## Makefile
```bash
make up     # Sobe o ambiente
make down   # Encerra o ambiente
make test   # Testa o endpoint com pergunta sobre composição
```