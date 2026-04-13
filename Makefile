up:
	docker compose up -d --build

down:
	docker compose down

test:
	@echo "=== Teste 1: O que é composição? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"O que é composição?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 2: Qual o papel da Tool de conhecimento? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Qual o papel da Tool de conhecimento?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 3: A tool deve responder diretamente ao usuário? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"A tool deve responder diretamente ao usuário?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 4: Pode resumir em uma frase? (histórico) ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Pode resumir em uma frase?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 5: Como agir sem contexto suficiente? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Como agir sem contexto suficiente?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 6: Quando usar herança? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Quando usar herança?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 7: Qual o papel da orquestração? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Qual o papel da orquestração?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 8: Onde colocar regra de negócio? ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Onde colocar regra de negócio, no endpoint ou no fluxo interno?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 9: Pode resumir o que falamos? (histórico completo) ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Pode resumir o que falamos?","session_id":"validacao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Teste 10: Isolamento de sessão (outra-sessao) ==="
	@curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"Pode resumir o que falamos?","session_id":"outra-sessao"}' | python3 -m json.tool --no-ensure-ascii
	@echo ""
	@echo "=== Todos os testes finalizados ==="