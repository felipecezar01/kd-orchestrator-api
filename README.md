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

> A aplicacao valida as variaveis de ambiente obrigatorias no startup. Se alguma estiver faltando, o container nao inicia e exibe quais variaveis estao ausentes.

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
  tool.py            # Busca contexto na KB via HTTP (com cache)
  llm_client.py      # Envia pergunta + contexto para o LLM
  exceptions.py      # Excecoes customizadas (KBError, LLMError)
test_api.py          # Script de testes cross-platform (Linux, macOS, Windows)
Makefile             # Atalhos: up, down, test
```

## Fluxo da aplicacao

1. O usuario envia uma mensagem via POST /messages
2. O Pydantic valida a entrada: message obrigatorio, nao pode ser vazio, maximo 1000 caracteres, campos extras sao rejeitados
3. O orquestrador limpa sessoes expiradas e recupera historico se houver session_id
4. O orquestrador chama a tool para buscar contexto na KB
5. A tool verifica se a KB esta em cache (TTL de 5 minutos); se nao, faz GET na KB_URL, parseia o markdown em secoes e retorna trechos relevantes
6. Se encontrou contexto: o orquestrador monta o prompt e chama o LLM, retornando answer + sources
7. Se nao encontrou contexto e nao tem historico de sessao: retorna fallback padrao sem chamar o LLM
8. Se nao encontrou contexto mas tem historico de sessao: chama o LLM com o historico para perguntas de continuidade
9. Apos a resposta do LLM, o sistema valida se a saida parece um fallback e padroniza a frase exata do contrato

## Regras de decisao do fluxo

- A tool e chamada sempre que ha uma message valida
- A busca filtra secoes por match de titulo com remocao de stop words para evitar falsos positivos
- O contexto retornado entra no LLM apenas se houver trechos relevantes
- Se nao houver contexto e nao houver historico, retorna fallback direto sem consumir chamada ao LLM
- Se houver historico de sessao, o LLM recebe o historico para responder perguntas de continuidade
- O LLM recebe instrucao para responder apenas com base no contexto fornecido
- Apos a resposta do LLM, o codigo valida a saida: se parecer com fallback, padroniza a frase exata e limpa os sources

## Validacao da entrada

O modelo `MessageRequest` aplica as seguintes validacoes antes do fluxo interno:

- `message` e obrigatorio e deve ser string
- Espacos no inicio e fim sao removidos (strip); se o resultado ficar vazio, retorna 422
- Mensagens acima de 1000 caracteres sao rejeitadas (protecao contra consumo excessivo de tokens)
- Campos extras alem de `message` e `session_id` sao proibidos (`extra="forbid"`)

## Session ID (diferencial)

A API aceita um campo opcional `session_id` na requisicao. Quando presente, o sistema mantem um historico curto da conversa em memoria, permitindo perguntas de continuidade como "pode resumir o que falamos?".

- Sessoes sao isoladas: cada session_id tem seu proprio historico
- Historico limitado a 10 mensagens por sessao (janela curta)
- Sessoes expiram apos 30 minutos de inatividade (TTL)
- Estrutura da sessao definida por `SessionData` (TypedDict com `history` e `last_access`)
- Armazenamento em memoria (dicionario Python): o historico e perdido se o container reiniciar
- Sem session_id, cada chamada e independente

## Tratamento de erros

O endpoint diferencia erros por origem usando excecoes customizadas:

- `KBError` (erro ao acessar a KB): retorna 502
- `LLMError` (erro do provider LLM): retorna 503
- Erros inesperados: retorna 500

Em todos os casos, o erro real e registrado nos logs do container com traceback completo (`logger.error` com `exc_info=True`), e o cliente recebe apenas uma mensagem generica, sem expor detalhes internos.

## Cache da KB

A tool mantem a KB em cache por 5 minutos (TTL). O cache e global da aplicacao (compartilhado entre todas as requests e sessoes). Isso evita fazer GET na KB a cada request, reduzindo latencia e carga na fonte.

## Decisoes tecnicas

- **FastAPI**: escolhido por gerar Swagger automatico, suportar async nativamente, e integrar validacao com Pydantic
- **httpx em vez de requests**: suporta chamadas assincronas, consistente com o fluxo async do FastAPI
- **OpenAI SDK apontando para Gemini**: o SDK da OpenAI funciona como cliente HTTP generico. Configurando base_url para o endpoint do Gemini, o mesmo codigo funciona com qualquer provider compativel
- **Busca por stop words em vez de TF-IDF ou embeddings**: a KB tem 14 secoes com titulos descritivos e curtos. Para esse escopo, match por titulo com filtragem de stop words e a abordagem mais pragmatica. Para uma KB maior, o proximo passo seria TF-IDF (scikit-learn) ou embeddings com banco vetorial
- **Validacao de fallback no codigo**: apos a resposta do LLM, o orquestrador verifica se o texto parece um fallback e padroniza a frase exata. Isso segue a recomendacao do desafio de nao confiar em temperature para garantir formato
- **Provider configuravel**: LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL e LLM_API_KEY sao variaveis de ambiente. Trocar de Gemini para outro provider compativel nao exige mudanca no codigo
- **Validacao de env no startup**: a aplicacao verifica todas as variaveis obrigatorias ao iniciar. Se alguma faltar, o container nao sobe (fail fast)
- **Excecoes customizadas**: KBError e LLMError permitem diferenciar a origem do erro no endpoint e retornar status codes semanticamente corretos (502, 503)
- **Cache da KB**: evita GET redundante a cada request, com TTL de 5 minutos como equilibrio entre economia e frescor dos dados
- **TypedDict para sessao**: tipagem explicita da estrutura de sessao sem overhead de runtime

## Makefile

```bash
make up     # Sobe o ambiente
make down   # Encerra o ambiente
make test   # Roda 10 testes automatizados via test_api.py
```

> No Windows, caso `make` nao esteja disponivel, rode `python test_api.py` diretamente.