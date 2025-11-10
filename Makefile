.PHONY: help install dev prod docker-build docker-up docker-down docker-logs test clean

# Couleurs pour le terminal
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help:
	@echo "$(GREEN)YouTube Manager - Commandes disponibles$(NC)"
	@echo ""
	@echo "$(YELLOW)Installation:$(NC)"
	@echo "  make install       - Installer les dépendances (backend + frontend)"
	@echo "  make install-backend - Installer les dépendances backend"
	@echo "  make install-frontend - Installer les dépendances frontend"
	@echo ""
	@echo "$(YELLOW)Développement:$(NC)"
	@echo "  make dev           - Démarrer backend + frontend + worker en dev"
	@echo "  make dev-backend   - Démarrer seulement le backend"
	@echo "  make dev-frontend  - Démarrer seulement le frontend"
	@echo "  make dev-worker    - Démarrer seulement le worker"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make docker-build  - Build les images Docker"
	@echo "  make docker-up     - Démarrer tous les services Docker"
	@echo "  make docker-down   - Arrêter tous les services Docker"
	@echo "  make docker-logs   - Voir les logs Docker"
	@echo "  make docker-prod   - Démarrer en mode production"
	@echo ""
	@echo "$(YELLOW)Utilitaires:$(NC)"
	@echo "  make test          - Lancer les tests"
	@echo "  make clean         - Nettoyer les fichiers temporaires"
	@echo "  make queue-status  - Voir le statut de la queue"
	@echo "  make queue-process - Traiter la queue manuellement"

install: install-backend install-frontend

install-backend:
	@echo "$(GREEN)Installation des dépendances backend...$(NC)"
	cd backend && python -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt

install-frontend:
	@echo "$(GREEN)Installation des dépendances frontend...$(NC)"
	cd frontend && yarn install

dev:
	@echo "$(GREEN)Démarrage de l'application en mode développement...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8001$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8001/docs$(NC)"
	@make -j3 dev-backend dev-frontend dev-worker

dev-backend:
	@echo "$(GREEN)Démarrage du backend...$(NC)"
	cd backend && . venv/bin/activate && uvicorn server:app --reload --port 8001

dev-frontend:
	@echo "$(GREEN)Démarrage du frontend...$(NC)"
	cd frontend && yarn start

dev-worker:
	@echo "$(GREEN)Démarrage du worker...$(NC)"
	cd backend && . venv/bin/activate && python workers/publication_worker.py

docker-build:
	@echo "$(GREEN)Build des images Docker...$(NC)"
	docker-compose build

docker-up:
	@echo "$(GREEN)Démarrage des services Docker...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)Services disponibles:$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend: http://localhost:8001"
	@echo "  API Docs: http://localhost:8001/docs"

docker-down:
	@echo "$(RED)Arrêt des services Docker...$(NC)"
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-prod:
	@echo "$(GREEN)Démarrage en mode production...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

test:
	@echo "$(GREEN)Lancement des tests...$(NC)"
	cd backend && . venv/bin/activate && pytest

queue-status:
	@echo "$(GREEN)Statut de la queue de publication:$(NC)"
	@curl -s http://localhost:8001/api/youtube/queue/status | jq .

queue-process:
	@echo "$(GREEN)Traitement manuel de la queue...$(NC)"
	@curl -s -X POST http://localhost:8001/api/youtube/queue/process | jq .

clean:
	@echo "$(RED)Nettoyage des fichiers temporaires...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Nettoyage terminé!$(NC)"
