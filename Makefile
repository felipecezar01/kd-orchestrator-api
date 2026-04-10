up:
	docker compose up -d --build

down:
	docker compose down

test:
	curl -s -X POST "http://localhost:8000/messages" \
		-H "Content-Type: application/json" \
		-d '{"message":"O que é composição?"}' | python3 -m json.tool