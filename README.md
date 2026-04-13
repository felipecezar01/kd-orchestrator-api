# KB Orchestrator API

Backend Python que orquestra um fluxo de busca em base de conhecimento (KB) com resposta gerada por LLM.

## Como executar

1. Clone o repositorio:
```bash
git clone https://github.com/felipecezar01/kd-orchestrator-api.git
cd kd-orchestrator-api
```

2. Configure as variaveis de ambiente:
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
- httpx (requisicoes HTTP assincronas)
- OpenAI SDK (compativel com Gemini via base_url)
- Docker + Docker Compose

## Estrutura do projeto

```
app/
  main.py           # Endpoint POST /messages, validacao com Pydantic
  orchestrator.py    # Orquestra o fluxo: tool -> LLM -> resposta
  tool.py            # Busca contexto na KB via HTTP
  llm_client.py      # Envia pergunta + contexto para o LLM
```

## Fluxo da aplicacao

1. O usuario envia uma mensagem via POST /messages
2. O Pydantic valida a entrada (message obrigatorio, nao pode ser vazio)
3. O orquestrador chama a tool para buscar contexto na KB
4. A tool faz GET na KB_URL, parseia o markdown em secoes e retorna trechos relevantes
5. Se encontrou contexto: o orquestrador monta o prompt e chama o LLM, retornando answer + sources
6. Se nao encontrou contexto e nao tem historico de sessao: retorna fallback padrao sem chamar o LLM
7. Se nao encontrou contexto mas tem historico de sessao: chama o LLM com o historico para perguntas de continuidade
8. Apos a resposta do LLM, o sistema valida se a saida parece um fallback e padroniza a frase exata do contrato

## Regras de decisao do fluxo

- A tool e chamada sempre que ha uma message valida
- A busca filtra secoes por match de titulo com remocao de stop words para evitar falsos positivos
- O contexto retornado entra no LLM apenas se houver trechos relevantes
- Se nao houver contexto e nao houver historico, retorna fallback direto sem consumir chamada ao LLM
- Se houver historico de sessao, o LLM recebe o historico para responder perguntas de continuidade
- O LLM recebe instrucao para responder apenas com base no contexto fornecido
- Apos a resposta do LLM, o codigo valida a saida: se parecer com fallback, padroniza a frase exata e limpa os sources

## Session ID (diferencial)

A API aceita um campo opcional session_id na requisicao. Quando presente, o sistema mantem um historico curto da conversa em memoria, permitindo perguntas de continuidade como "pode resumir o que falamos?".

- Sessoes sao isoladas: cada session_id tem seu proprio historico
- Historico limitado a 10 mensagens por sessao (janela curta)
- Armazenamento em memoria (dicionario Python): o historico e perdido se o conteiner reiniciar
- Sem session_id, cada chamada e independente

## Decisoes tecnicas

- FastAPI: escolhido por gerar Swagger automatico, suportar async nativamente, e integrar validacao com Pydantic
- httpx em vez de requests: suporta chamadas assincronas, consistente com o fluxo async do FastAPI
- OpenAI SDK apontando para Gemini: o SDK da OpenAI funciona como cliente HTTP generico. Configurando base_url para o endpoint do Gemini, o mesmo codigo funciona com qualquer provider compativel
- Busca por stop words em vez de TF-IDF ou embeddings: a KB tem 14 secoes com titulos descritivos e curtos. Para esse escopo, match por titulo com filtragem de stop words e a abordagem mais pragmatica. Para uma KB maior, o proximo passo seria TF-IDF (scikit-learn) ou embeddings com banco vetorial
- Validacao de fallback no codigo: apos a resposta do LLM, o orquestrador verifica se o texto parece um fallback e padroniza a frase exata. Isso segue a recomendacao do desafio de nao confiar em temperature para garantir formato
- Provider configuravel: LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL e LLM_API_KEY sao variaveis de ambiente. Trocar de Gemini para outro provider compativel nao exige mudanca no codigo

## Makefile

```bash
make up     # Sobe o ambiente
make down   # Encerra o ambiente
make test   # Testa o endpoint com pergunta sobre composicao
```