# 📖 Documentation API - GeoProd_CM

L'API de GeoProd_CM est construite avec **Django REST Framework** et fournit des données structurées pour la cartographie et l'analyse.

## 🔑 Points d'Entrée (Endpoints)

### 1. Productions
`GET /api/productions/`
- **Description** : Liste paginée de toutes les entrées de production.
- **Filtres** : `secteur`, `produit`, `annee`, `region`, `departement`, `arrondissement`.
- **Pagination** : 20 résultats par défaut.

### 2. Statistiques (Synthèse)
`GET /api/productions/statistiques/`
- **Description** : Retourne les agrégations filtrées pour le dashboard.
- **Champs retournés** : `total_productions`, `total_quantite`, `par_secteur`, `zone_dominante`.

### 3. Données Cartographiques
`GET /api/productions/map_data/`
- **Description** : Retourne un GeoJSON optimisé pour Leaflet.
- **Paramètres** : 
  - `niveau` : `region`, `departement` ou `arrondissement`.
  - `secteur`, `produit`, `annee`.

### 4. Autocomplétion de Lieux
`GET /api/productions/autocomplete/`
- **Description** : Recherche textuelle dans la hiérarchie administrative.
- **Paramètre** : `q` (minimum 2 caractères).

### 5. Export Excel
`GET /api/productions/export_excel/`
- **Description** : Génère un fichier `.xlsx` formaté basé sur les filtres actuels.
- **Nom du fichier** : `export_[secteur]_[produit]_[annee]_geoprod_cm.xlsx`.

## 📍 Géographie

### Régions / Départements / Arrondissements
`GET /api/regions/` | `GET /api/departements/` | `GET /api/arrondissements/`
- Accès direct aux listes administratives et leurs géométries respectives.

## 🛠️ Développement & Test
Tous les endpoints supportent l'interface **Browsable API** de DRF pour faciliter le test direct via le navigateur.
