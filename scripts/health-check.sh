#!/bin/bash

# Script de vérification de santé de l'application

echo "🏋️  Vérification de santé de YouTube Manager"
echo ""

# Backend
echo "1️⃣  Backend API..."
if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ Backend actif (http://localhost:8001)"
else
    echo "   ❌ Backend inactif"
fi

# Frontend
echo "2️⃣  Frontend..."
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend actif (http://localhost:3000)"
else
    echo "   ❌ Frontend inactif"
fi

# Queue
echo "3️⃣  Queue de publication..."
QUEUE_STATUS=$(curl -s http://localhost:8001/api/youtube/queue/status 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ Queue accessible"
    echo "$QUEUE_STATUS" | jq . 2>/dev/null
else
    echo "   ❌ Queue inaccessible"
fi

echo ""
echo "✅ Vérification terminée"
