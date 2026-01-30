#!/bin/sh

# Quitter si une commande échoue
set -e

echo "➡️ Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "➡️ Application des migrations..."
python manage.py migrate --noinput

echo "➡️ Lancement de Gunicorn..."
exec "$@"
