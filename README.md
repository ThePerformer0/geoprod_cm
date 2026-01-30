# 🌍 GeoProd_CM - Plateforme SIG des Bassins de Production

## 📋 Description
**GeoProd_CM** est une plateforme web SIG institutionnelle de pointe conçue pour la visualisation, l'analyse et l'exportation des données de production économique (Agriculture, Élevage, Pêche) sur l'ensemble du territoire camerounais.

## 🚀 Fonctionnalités Clés

### 🗺️ Carte Interactive (Leaflet)
- **Visualisation Choroplèthe** : Analyse visuelle de la production par Région, Département ou Arrondissement.
- **Sidebars Intelligentes** : Filtres avancés (Secteur, Produit, Année) et panneau d'informations contextuelles.
- **Interactivité** : Tooltips dynamiques et détails au clic sur les zones géographiques.

### 📊 Analyse et Données
- **Dashboard de Synthèse** : Vue d'ensemble immédiate des indicateurs clés (Production totale, zone dominante, records).
- **Tableaux Dynamiques** : Consultation structurée des données avec pagination optimisée (20 records/page).
- **Recherche Instantanée** : Autocomplétion intelligente des lieux (Régions, Départements, Arrondissements).
- **Export Excel** : Génération de fichiers Excel avec noms dynamiques et formatage professionnel.

### 🎨 Design & Marque
- **Identité Visuelle** : Logo personnalisé aux couleurs nationales du Cameroun.
- **UI Premium** : Thème vert agricole, design responsive et animations fluides avec Tailwind CSS.

## 🏗️ Architecture Technique

- **Backend** : Django 4.2 + Django REST Framework.
- **Performance** : Utilisation de `select_related` et pagination serveur pour des temps de réponse ultra-rapides.
- **Servage Statique** : Whitenoise configuré pour la production (compression & cache).
- **Base de données** : PostgreSQL avec gestion des géométries JSON (compatible Cloud/Neon).
- **Frontend** : Vanilla JavaScript, Leaflet.js, Tailwind CSS, Font Awesome.

## 🚀 Installation & Déploiement

### Prérequis
- Python 3.8+
- PostgreSQL
- `pip install -r requirements.txt`

### Variables d'Environnement (.env)
```env
DEBUG=False
SECRET_KEY=votre_cle_secrete
DATABASE_URL=postgresql://user:password@host/dbname
ALLOWED_HOSTS=votre_domaine.com,localhost
```

### Lancement Local
```bash
# Dans le dossier backend/
python manage.py migrate
python manage.py runserver
```

### Commandes de Gestion (Import Données)
```bash
# Importer les géométries (GeoJSON)
python manage.py import_geometries

# Générer des données de test réalistes
python manage.py import_sample_productions
```

## 🔧 Dépendances Principales
- `Django`, `djangorestframework`
- `whitenoise`, `gunicorn`
- `openpyxl` (Export Excel)
- `dj-database-url`, `python-dotenv`

---
© 2026 - **GeoProd_CM** | SIG Bassins de Production Cameroun
