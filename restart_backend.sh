#!/bin/bash

echo "🔄 Redémarrage du backend..."

# Redémarrer le backend avec supervisor
sudo supervisorctl restart backend

# Attendre 3 secondes
sleep 3

# Vérifier le statut
echo ""
echo "📊 Statut des services:"
sudo supervisorctl status backend

# Tester l'API
echo ""
echo "🏥 Test de santé de l'API..."
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ Backend opérationnel sur http://localhost:8001"
    echo "📖 Documentation API: http://localhost:8001/docs"
else
    echo "❌ Backend ne répond pas"
    echo "📝 Voir les logs: tail -f /var/log/supervisor/backend.err.log"
fi
