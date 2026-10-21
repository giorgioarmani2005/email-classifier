.PHONY: all run clear setting_env

COMPOSE=./docker/docker-compose.yaml

all: setting_env run


run: $(COMPOSE)
	docker compose --env-file ./.env -f $(COMPOSE) up -d --build


clear: $(COMPOSE)
	docker compose  -f $(COMPOSE) down -v --rmi all --remove-orphans


setting_env: .env.example
	cp .env.example .env