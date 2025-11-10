#!/bin/bash

# Script de démarrage rapide pour YouTube Manager

set -e

echo "======================================"
echo "🚀 YouTube Manager - Démarrage"
echo "======================================"
echo ""

# Vérifier si Docker est installé
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker détecté"
    echo "1. Démarrage avec Docker (recommandé)"
    echo "2. Démarrage local (sans Docker)"
    echo ""
    read -p "Choisissez une option (1 ou 2): " choice
    
    if [ "$choice" = "1" ]; then
        echo ""
        echo "🔧 Build des images..."
        docker-compose build
        
        echo ""
        echo "✅ Démarrage des services..."
        docker-compose up -d
        
        echo ""
        echo "======================================"
        echo "✅ Application démarrée avec succès!"
        echo "======================================"
        echo ""
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔌 Backend API: http://localhost:8001"
        echo "📚 API Docs: http://localhost:8001/docs"
        echo ""
        echo "Voir les logs: docker-compose logs -f"
        echo "Arrêter: docker-compose down"
        
        exit 0
    fi
fi

echo "💻 Démarrage local"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Erreur: Node.js n'est pas installé"
    exit 1
fi

echo "✅ Python $(python3 --version)"
echo "✅ Node $(node --version)"
echo ""

# Backend
echo "1️⃣  Installation backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Backend prêt"
echo ""

# Frontend
echo "2️⃣  Installation frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    yarn install
fi

echo "✅ Frontend prêt"
echo ""

echo "======================================"
echo "🚀 Démarrage des services"
echo "======================================"
echo ""
echo "Ouvrez 3 terminaux et lancez:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend && source venv/bin/activate && uvicorn server:app --reload --port 8001"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && yarn start"
echo ""
echo "Terminal 3 (Worker):"
echo "  cd backend && source venv/bin/activate && python workers/publication_worker.py"
echo ""
echo "Ou utilisez: make dev"
echo ""
