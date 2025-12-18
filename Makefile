export COMPOSE_NAME=sistema_base_backend_v2
export TEST_COMPOSE_NAME=sistema_base_backend_v2_test

ruff:
	ruff format . && ruff check . --fix

compose:
	docker-compose -f docker-compose.yml -p $(COMPOSE_NAME) up --build -d

compose-down:
	docker-compose -f docker-compose.yml -p $(COMPOSE_NAME) down

test-compose:
	docker-compose -f docker-compose.test.yml -p $(TEST_COMPOSE_NAME) up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml -p $(TEST_COMPOSE_NAME) down

test-compose-down:
	docker-compose -f docker-compose.test.yml -p $(TEST_COMPOSE_NAME) down -v

test-local:
	TEST_ENV=true pytest tests/ -v --tb=short

test-unit:
	TEST_ENV=true pytest tests/unitarios/ -v --tb=short

test-integration:
	TEST_ENV=true pytest tests/integracao/ -v --tb=short

sync:
	uv sync