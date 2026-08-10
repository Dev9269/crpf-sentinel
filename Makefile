.PHONY: up down logs backend frontend seed demo simulate test agent

up: ## Start full stack (postgres + backend + frontend)
	docker compose up -d --build

down: ## Stop everything
	docker compose down

logs: ## Tail all logs
	docker compose logs -f

backend: ## Run backend locally (uses SQLite by default)
	cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

frontend: ## Run frontend locally
	cd frontend && npm install && npm run dev

seed: ## Seed demo data + rules
	cd backend && python -m app.seed.seed_all

SCENARIO ?= brute_force

simulate: ## Run a demo attack scenario (default: brute_force, override with make simulate SCENARIO=powershell)
	cd backend && python -m app.simulation.run $(SCENARIO)

agent: ## Run the Windows collector agent (needs SENTINEL_API_TOKEN)
	cd agent && pip install -r requirements.txt && SENTINEL_API_TOKEN="$(AGENT_API_TOKEN)" python -m main --simulate
