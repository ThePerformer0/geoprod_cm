# 🌍 Plateforme SIG des Bassins de Production - Cameroun

## 📋 Description
Plateforme web SIG institutionnelle pour visualiser et analyser les bassins de production économique du Cameroun (agriculture, élevage, pêche).

## 🎯 Objectif
Développer un outil de visualisation cartographique et d'analyse des données de production par bassins économiques et niveaux administratifs.

## 🏗️ Architecture
- **Backend** : Django + Django REST Framework
- **Base de données** : PostgreSQL/PostGIS (Neon.tech)
- **Frontend** : HTML/CSS/JavaScript + Leaflet
- **API** : RESTful JSON

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL avec PostGIS
- Git

### Installation locale
```bash
# Cloner le dépôt
git clone [url-du-repo]

# Créer un environnement virtuel
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Lancer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

```

## 📁 Structure du projet

    backend/
    ├── config/           # Configuration Django
    ├── geoprod_cm/       # Application principale
    ├── static/           # Fichiers statiques
    ├── templates/        # Templates HTML
    ├── requirements.txt  # Dépendances Python
    └── manage.py         # Script de gestion

## 🔧 Technologies utilisées

- **Backend** : Django 4.2, Django REST Framework

- **Base de données** : PostgreSQL/PostGIS

- **Cartographie** : Leaflet.js

- **Visualisation** : Chart.js

## 👥 Auteurs
