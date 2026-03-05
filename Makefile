DOCKER_COMPOSE ?= docker compose
FRONTEND_DIR := chauffage/frontend

.PHONY: start build frontend-dev stop clean

start:
	$(DOCKER_COMPOSE) up --build chauffage

frontend-dev:
	$(DOCKER_COMPOSE) up frontend-dev

build:
	docker run --rm -v $(PWD)/$(FRONTEND_DIR):/app -w /app node:20-slim \
		sh -c "npm install && npm run build"

stop:
	$(DOCKER_COMPOSE) down

clean:
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/dist
