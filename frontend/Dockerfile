# Dockerfile pour le Frontend React
FROM node:18-alpine AS build

# Répertoire de travail
WORKDIR /app

# Copier package.json et yarn.lock
COPY package.json yarn.lock ./

# Installer les dépendances
RUN yarn install --frozen-lockfile

# Copier le code source (exclure .env pour éviter les conflits)
COPY . .
# Supprimer le fichier .env s'il existe pour éviter les conflits avec les variables d'environnement Docker
RUN rm -f .env

# Build de production
RUN yarn build

# Stage de production avec nginx
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Copier la configuration nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port
EXPOSE 3000

# Démarrer nginx
CMD ["nginx", "-g", "daemon off;"]
