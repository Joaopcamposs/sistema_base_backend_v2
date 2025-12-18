export COMPOSE_NAME=sistema_base_backend_v2

ruff:
	ruff format . && ruff check . --fix

compose:
	docker-compose -f docker-compose.yml -p $(COMPOSE_NAME) up --build -d