# Dockerfile pour le Backend FastAPI
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    IMAGEMAGICK_BINARY=/usr/bin/convert

# Installer les dépendances système incluant ImageMagick
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    imagemagick \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    fonts-noto-color-emoji \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Vérifier l'installation et configurer ImageMagick
RUN echo "=== Version d'ImageMagick installée ===" && \
    convert -version && \
    echo "=== Configuration d'ImageMagick ===" && \
    # Trouver et configurer le fichier policy.xml
    POLICY_FILE=$(find /etc -name policy.xml 2>/dev/null | head -n 1) && \
    if [ -n "$POLICY_FILE" ]; then \
    echo "Fichier de politique trouvé: $POLICY_FILE" && \
    # Autoriser la lecture/écriture pour les patterns courants
    sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/g' "$POLICY_FILE" && \
    sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' "$POLICY_FILE" && \
    sed -i 's/rights="none" pattern="XPS"/rights="read|write" pattern="XPS"/g' "$POLICY_FILE" || true; \
    else \
    echo "Aucun fichier policy.xml trouvé"; \
    fi

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY backend/requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY backend/ .

# Créer les répertoires nécessaires
RUN mkdir -p /app/ressources/videos /app/ressources/audio /app/ressources/thumbnails

# Exposer le port
EXPOSE 8001

# Commande de démarrage
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]