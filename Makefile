.PHONY: all run clear setting_env send-eml

COMPOSE=./docker/docker-compose.yaml

all: setting_env run

TEST_EML:=$(wildcard eml_example/*.eml)
COOKIE_FILE ?= cookies.txt
LIMIT ?= 3

run: $(COMPOSE)
	docker compose --env-file ./.env -f $(COMPOSE) up -d --build


clear: $(COMPOSE)
	docker compose  -f $(COMPOSE) down -v --rmi all --remove-orphans


send-eml:
	@count=0; \
	for file in $(TEST_EML); do \
		if [ $$count -ge $(LIMIT) ]; then break; fi; \
		echo "Отправка $$file..."; \
		curl -X POST http://127.0.0.1:8000/api/v1/upload \
		-H "accept: application/json" \
		-c $(COOKIE_FILE) \
		-b $(COOKIE_FILE) \
		-F "files=@$$file"; \
		echo ""; \
		count=$$((count + 1)); \
	done

analyze-eml:
	curl -X POST http://127.0.0.1:8000/api/v1/analyze/files \
	-b $(COOKIE_FILE) \
	-H "accept: application/json"
	@echo ""

setting_env: .env.example
	cp .env.example .env