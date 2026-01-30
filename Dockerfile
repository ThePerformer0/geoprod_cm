# Utiliser une image Python officielle légère
FROM python:3.11-slim as builder

# Définir le dossier de travail
WORKDIR /app

# Empêcher Python d'écrire des fichiers .pyc et assurer l'affichage immédiat des logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installer les dépendances système nécessaires pour psycopg2 et autres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python via wheel pour accélérer la build finale
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --- Stage Final ---
FROM python:3.11-slim

# Créer un utilisateur non-privilégié pour la sécurité
RUN addgroup --system django && adduser --system --group django

WORKDIR /app

# Installer les outils nécessaires pour le runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Récupérer les wheels de la phase de build
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copier le reste du projet
COPY . .

# Définir le dossier de travail sur backend
WORKDIR /app/backend

# S'assurer que l'entrypoint est exécutable
USER root
RUN chmod +x /app/entrypoint.sh
RUN chown -R django:django /app
USER django

# Exposer le port 8000
EXPOSE 8000

# Utiliser l'entrypoint pour les migrations et le collectstatic
ENTRYPOINT ["/app/entrypoint.sh"]

# Utiliser Gunicorn pour servir l'application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
