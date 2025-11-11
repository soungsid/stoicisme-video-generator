# Dockerfile pour le Backend FastAPI
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    IMAGEMAGICK_BINARY=/usr/bin/convert

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    gnupg \
    software-properties-common \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    fonts-noto-color-emoji \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Ajouter le dépôt ImageMagick et installer la dernière version
RUN apt-get update && apt-get install -y imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Vérifier la version installée et configurer ImageMagick
RUN convert -version && \
    # Trouver le fichier policy.xml (peut être dans ImageMagick-6 ou ImageMagick-7)
    POLICY_FILE=$(find /etc -name policy.xml 2>/dev/null | head -n 1) && \
    if [ -n "$POLICY_FILE" ]; then \
    echo "Configuration de $POLICY_FILE" && \
    sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@*"/g' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PDF"/<policy domain="coder" rights="read|write" pattern="PDF"/g' "$POLICY_FILE" || true; \
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