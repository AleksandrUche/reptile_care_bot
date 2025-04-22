TARGET_DIRS := .
LOCAL_MAKEFILE := Makefile.local
DB_NAME := rassrochki_api_db

# ruff check --config "pyproject.toml" --fix


format:
	ruff format $(TARGET_DIRS)

lint:
	ruff format --check $(TARGET_DIRS)
	ruff check $(TARGET_DIRS) --fix

test:
	poetry run pytest --cov

mm:
	docker compose exec rassrochki alembic revision --autogenerate

migrate:
	docker compose exec rassrochki alembic upgrade head

up:
	docker compose up --build

down:
	docker compose down

up_db:
	docker compose up -d api-db

run_app:
	docker compose up rassrochki --build

logs_app:
	docker compose logs -f rassrochki

logs_db:
	docker compose logs -f api-db

.PHONY: check_active_service
check_active_service:
	@status=$$(docker compose ps --services --filter "status=running" | grep -w "$(service)"); \
	if [ -z "$$status" ]; then \
	echo -e "❌ Container for service \033[1;31m$(service)\033[0m isn't running"; \
	exit 1; \
	fi; \
	echo -e "🐋 Container for service \033[1;31m$(service)\033[0m is active";

.PHONY: close_db_connections
close_db_connections:
	@$(MAKE) -s check_active_service service="api-db"
	@echo "🔌 Closing all connections to the database...";
	@docker compose exec -i api-db psql -U postgres -d $(DB_NAME) \
	-c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$(DB_NAME)' AND pid <> pg_backend_pid();" 2>/dev/null || true
	@echo "✅ All connections to the database are closed!";

.PHONY: createdb
createdb:
	@$(MAKE) -s check_active_service service="api-db"
	@echo "🏗️ Creating database...";
	@docker compose exec -i api-db createdb -U postgres $(DB_NAME)
	@echo "✅ Database created successfully!";

.PHONY: dropdb
dropdb: close_db_connections
	@$(MAKE) -s check_active_service service="api-db"
	@echo "🗑️ DB_NAME = $(DB_NAME)";
	@docker compose exec -i api-db dropdb -U postgres $(DB_NAME) 2>/dev/null || true
	@echo "✅ Database dropped successfully!";

.PHONY: restore_dump
restore_dump:
	@echo "⏳️ Start restoring dump...";
	@if [ -z "$(path)" ]; then \
		echo "❌ Error: no path param"; \
		exit 1; \
	fi
	@if [ ! -f $(path) ]; then \
		echo "❌ Error: No file in path $(path)"; \
		exit 1; \
	fi
	@if [ -z "$(DB_NAME)" ]; then \
		echo "❌ Error: DB_NAME is not set"; \
		exit 1; \
	fi
	@$(MAKE) -s dropdb createdb
	@cat $(path) | docker compose exec -T api-db psql -U postgres -d $(DB_NAME) || (echo "❌ Error while restoring backup!" && exit 1)
	@echo "✅ Dump restored and permissions granted successfully!";

.PHONY: venv_uv
venv_uv:  ## Создание виртуального окружения и установка backend зависимостей при помощи uv
	uv venv && \
	source .venv/bin/activate && \
	export UV_INDEX_URL=$(UV_INDEX_URL) && \
	export UV_HTTP_TIMEOUT=120 && \
	uv pip install --no-cache -r requirements.txt

.PHONY: lock
lock:
	uv pip compile \
		--index-url=$(UV_INDEX_URL) \
		--no-cache \
		pyproject.toml -o requirements.txt

.PHONY: venv_sync
venv_sync:  ## Синхронизация зависимостей виртуального окружения из requirements.txt (с очисткой кеша)
	source .venv/bin/activate && \
	export UV_INDEX_URL=$(UV_INDEX_URL) && \
	uv pip sync --no-cache requirements.txt
