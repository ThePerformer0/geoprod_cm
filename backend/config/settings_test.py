"""
Settings de test : SQLite en memoire + StaticFiles simple (pas de manifest).
Usage : python manage.py test --settings=config.settings_test
"""
from config.settings import *

# Base de donnees SQLite en memoire pour les tests (rapide, sans DATABASE_URL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Desactiver le CompressedManifestStaticFilesStorage (cherche staticfiles.json)
# et utiliser le backend simple pour les tests
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Desactiver les warnings de migration pendant les tests
MIGRATION_MODULES = {}
