// ============================================================================
// CARTE INTERACTIVE - BASSINS DE PRODUCTION CAMEROUN
// ============================================================================

// Configuration globale
const API_BASE_URL = '/api/productions';
const MAP_CENTER = [7.3697, 12.3547]; // Centre du Cameroun
const MAP_ZOOM = 6;

// Listes prédéfinies de produits par secteur (optimisation)
const PRODUITS_PAR_SECTEUR = {
    agriculture: [
        'Maïs',
        'Riz',
        'Manioc',
        'Banane plantain',
        'Cacao',
        'Café',
        'Coton',
        'Arachide',
        'Sorgho',
        'Mil',
        'Igname',
        'Macabo',
        'Haricot',
        'Tomate',
        'Oignon'
    ],
    elevage: [
        'Bovins',
        'Ovins',
        'Caprins',
        'Porcins'
    ],
    peche: [
        'Pêche maritime',
        'Pêche en eau douce',
        'Pêche lacustre',
        'Pêche fluviale',
        'Tilapia',
        'Silure',
        'Carpe',
        'Crevettes'
    ]
};

// Variables globales
let map = null;
let currentLayer = null;
let currentFilters = {
    secteur: '',
    produit: '',
    annee: '',
    niveau: 'region'
};

// ============================================================================
// INITIALISATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    initMap();
    initSidebarToggles();
    loadFilterOptions();
    setupEventListeners();
    showNoDataMessage();
});

// ============================================================================
// CARTE LEAFLET
// ============================================================================

function initMap() {
    // Initialiser la carte
    map = L.map('map', {
        center: MAP_CENTER,
        zoom: MAP_ZOOM,
        zoomControl: true
    });

    // Ajouter le fond de carte (CartoDB Positron - sobre et institutionnel)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);
}

// ============================================================================
// GESTION DES SIDEBARS
// ============================================================================

function initSidebarToggles() {
    const toggleLeft = document.getElementById('toggle-left');
    const toggleRight = document.getElementById('toggle-right');
    const sidebarLeft = document.getElementById('sidebar-left');
    const sidebarRight = document.getElementById('sidebar-right');

    toggleLeft.addEventListener('click', function () {
        sidebarLeft.classList.toggle('collapsed');
        const icon = toggleLeft.querySelector('i');
        icon.classList.toggle('fa-chevron-left');
        icon.classList.toggle('fa-chevron-right');

        // Redimensionner la carte après l'animation
        setTimeout(() => map.invalidateSize(), 300);
    });

    toggleRight.addEventListener('click', function () {
        sidebarRight.classList.toggle('collapsed');
        const icon = toggleRight.querySelector('i');
        icon.classList.toggle('fa-chevron-right');
        icon.classList.toggle('fa-chevron-left');

        // Redimensionner la carte après l'animation
        setTimeout(() => map.invalidateSize(), 300);
    });

    // Permettre de cliquer sur les icônes pour déplier
    const leftIcons = sidebarLeft.querySelectorAll('.sidebar-icons .icon-item');
    leftIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            if (sidebarLeft.classList.contains('collapsed')) {
                toggleLeft.click();
            }
        });
    });

    const rightIcons = sidebarRight.querySelectorAll('.sidebar-icons .icon-item');
    rightIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            if (sidebarRight.classList.contains('collapsed')) {
                toggleRight.click();
            }
        });
    });
}

// ============================================================================
// CHARGEMENT DES OPTIONS DE FILTRES
// ============================================================================

async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/filtres/`);
        const data = await response.json();

        // Charger les années
        const anneeSelect = document.getElementById('annee');
        data.annees.forEach(annee => {
            const option = document.createElement('option');
            option.value = annee;
            option.textContent = annee;
            anneeSelect.appendChild(option);
        });

        // Sélectionner l'année la plus récente par défaut
        if (data.annees.length > 0) {
            anneeSelect.value = data.annees[0];
        }

    } catch (error) {
        console.error('Erreur lors du chargement des filtres:', error);
        showError('Erreur lors du chargement des options de filtres');
    }
}

// ============================================================================
// GESTION DES ÉVÉNEMENTS
// ============================================================================

function setupEventListeners() {
    // Changement de secteur -> charger les produits prédéfinis (INSTANTANÉ)
    document.getElementById('secteur').addEventListener('change', function () {
        const secteur = this.value;
        const produitSelect = document.getElementById('produit');

        if (!secteur) {
            produitSelect.innerHTML = '<option value="">-- Sélectionner un secteur d\'abord --</option>';
            produitSelect.disabled = true;
            return;
        }

        // Charger instantanément les produits prédéfinis
        const produits = PRODUITS_PAR_SECTEUR[secteur] || [];

        produitSelect.innerHTML = '<option value="">-- Tous les produits --</option>';
        produits.forEach(produit => {
            const option = document.createElement('option');
            option.value = produit;
            option.textContent = produit;
            produitSelect.appendChild(option);
        });

        produitSelect.disabled = false;
    });

    // Soumission du formulaire
    document.getElementById('filter-form').addEventListener('submit', function (e) {
        e.preventDefault();
        applyFilters();
    });

    // Réinitialisation des filtres
    document.getElementById('reset-filters').addEventListener('click', function () {
        document.getElementById('filter-form').reset();
        document.getElementById('produit').disabled = true;
        document.getElementById('produit').innerHTML = '<option value="">-- Sélectionner un secteur d\'abord --</option>';

        if (currentLayer) {
            map.removeLayer(currentLayer);
            currentLayer = null;
        }

        hideInfoSidebar();
        showNoDataMessage();

        // Cacher la légende
        document.getElementById('legend').classList.add('hidden');
    });
}

// ============================================================================
// APPLICATION DES FILTRES ET CHARGEMENT DES DONNÉES
// ============================================================================

async function applyFilters() {
    // Récupérer les valeurs des filtres
    currentFilters = {
        secteur: document.getElementById('secteur').value,
        produit: document.getElementById('produit').value,
        annee: document.getElementById('annee').value,
        niveau: document.getElementById('niveau').value
    };

    // Validation
    if (!currentFilters.secteur || !currentFilters.annee) {
        alert('Veuillez sélectionner au moins un secteur et une année');
        return;
    }

    // Afficher le loading
    showLoading();
    hideNoDataMessage();

    try {
        // Construire l'URL avec les paramètres
        const params = new URLSearchParams();
        if (currentFilters.secteur) params.append('secteur', currentFilters.secteur);
        if (currentFilters.produit) params.append('produit', currentFilters.produit);
        if (currentFilters.annee) params.append('annee', currentFilters.annee);
        if (currentFilters.niveau) params.append('niveau', currentFilters.niveau);

        // Utiliser l'endpoint optimisé map_data
        const response = await fetch(`${API_BASE_URL}/map_data/?${params.toString()}`, {
            signal: AbortSignal.timeout(30000) // Timeout de 30 secondes
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Afficher les données sur la carte
        displayMapData(data);

        // Afficher les informations dans la sidebar droite
        displayInfo(data.metadata);

        hideLoading();

    } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
        hideLoading();
        if (error.name === 'TimeoutError') {
            showError('Le chargement des données a pris trop de temps. Veuillez réessayer.');
        } else {
            showError('Erreur lors du chargement des données cartographiques. Veuillez réessayer.');
        }
    }
}

// ============================================================================
// AFFICHAGE DES DONNÉES SUR LA CARTE (CHOROPLÈTHE)
// ============================================================================

function displayMapData(geojsonData) {
    // Supprimer la couche précédente si elle existe
    if (currentLayer) {
        map.removeLayer(currentLayer);
    }

    // Vérifier s'il y a des données
    if (!geojsonData.features || geojsonData.features.length === 0) {
        showNoDataMessage();
        return;
    }

    // Calculer les classes de couleurs (méthode quantiles)
    const values = geojsonData.features
        .map(f => f.properties.quantite)
        .filter(v => v > 0)
        .sort((a, b) => a - b);

    const colorScale = getColorScale(values);

    // Créer la couche GeoJSON
    currentLayer = L.geoJSON(geojsonData, {
        style: function (feature) {
            return {
                fillColor: getColor(feature.properties.quantite, colorScale),
                weight: 2,
                opacity: 1,
                color: '#ffffff',
                fillOpacity: 0.7
            };
        },
        onEachFeature: function (feature, layer) {
            // Tooltip au survol
            const props = feature.properties;
            const tooltipContent = `
                <strong>${props.nom}</strong><br>
                ${formatNumber(props.quantite)} ${props.unite}
            `;
            layer.bindTooltip(tooltipContent);

            // Événements
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: selectFeature
            });
        }
    }).addTo(map);

    // Ajuster la vue sur les données
    map.fitBounds(currentLayer.getBounds());

    // Afficher la légende
    displayLegend(colorScale, geojsonData.metadata.unite);
}

// ============================================================================
// SYSTÈME DE COULEURS (CHOROPLÈTHE) - Thème Vert
// ============================================================================

function getColorScale(values) {
    if (values.length === 0) return [];

    // Calculer les quantiles
    const n = Math.min(5, values.length);
    const scale = [];

    for (let i = 0; i < n; i++) {
        const index = Math.floor((i / n) * values.length);
        scale.push(values[index]);
    }

    return scale;
}

function getColor(value, scale) {
    // Palette de couleurs (vert clair -> vert foncé) - Thème agricole
    const colors = ['#d1fae5', '#86efac', '#4ade80', '#22c55e', '#15803d'];

    if (!value || value === 0) return '#e5e7eb'; // Gris pour pas de données

    for (let i = scale.length - 1; i >= 0; i--) {
        if (value >= scale[i]) {
            return colors[i] || colors[colors.length - 1];
        }
    }

    return colors[0];
}

// ============================================================================
// INTERACTIONS AVEC LA CARTE
// ============================================================================

function highlightFeature(e) {
    const layer = e.target;
    layer.setStyle({
        weight: 3,
        color: '#16a34a',
        fillOpacity: 0.9
    });
    layer.bringToFront();
}

function resetHighlight(e) {
    currentLayer.resetStyle(e.target);
}

function selectFeature(e) {
    const props = e.target.feature.properties;

    // Afficher les détails dans la sidebar droite
    document.getElementById('zone-nom').textContent = props.nom;
    document.getElementById('zone-production').textContent =
        `${formatNumber(props.quantite)} ${props.unite}`;

    // Afficher la hiérarchie si disponible
    if (props.region_nom || props.departement_nom) {
        let hierarchie = [];
        if (props.region_nom) hierarchie.push(props.region_nom);
        if (props.departement_nom) hierarchie.push(props.departement_nom);
        hierarchie.push(props.nom);

        document.getElementById('zone-hierarchie-text').textContent = hierarchie.join(' > ');
        document.getElementById('zone-hierarchie').classList.remove('hidden');
    } else {
        document.getElementById('zone-hierarchie').classList.add('hidden');
    }

    document.getElementById('zone-details').classList.remove('hidden');
    showInfoSidebar();
}

// ============================================================================
// AFFICHAGE DES INFORMATIONS
// ============================================================================

function displayInfo(metadata) {
    // Titre
    const produitText = metadata.produit || 'Tous les produits';
    const niveauText = metadata.niveau === 'region' ? 'Régions' :
        metadata.niveau === 'departement' ? 'Départements' : 'Arrondissements';

    document.getElementById('info-title').innerHTML = `
        <i class="fas fa-chart-bar mr-2 text-green-600"></i>
        ${metadata.secteur ? metadata.secteur.charAt(0).toUpperCase() + metadata.secteur.slice(1) : 'Production'}
    `;
    document.getElementById('info-subtitle').textContent =
        `${produitText} - ${niveauText} - ${metadata.annee}`;

    // Indicateurs
    document.getElementById('total-production').textContent =
        `${formatNumber(metadata.total_production)} ${metadata.unite}`;
    document.getElementById('zone-dominante').textContent =
        metadata.zone_dominante || 'N/A';
    document.getElementById('nombre-zones').textContent = metadata.nombre_zones;

    showInfoSidebar();
}

function displayLegend(scale, unite) {
    const legendContent = document.getElementById('legend-content');
    const legend = document.getElementById('legend');

    legendContent.innerHTML = '';

    const colors = ['#d1fae5', '#86efac', '#4ade80', '#22c55e', '#15803d'];

    for (let i = 0; i < scale.length; i++) {
        const item = document.createElement('div');
        item.className = 'legend-item';

        const colorBox = document.createElement('div');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = colors[i];

        const label = document.createElement('span');
        label.className = 'text-xs text-gray-700';

        if (i === scale.length - 1) {
            label.textContent = `≥ ${formatNumber(scale[i])} ${unite}`;
        } else {
            label.textContent = `${formatNumber(scale[i])} - ${formatNumber(scale[i + 1])} ${unite}`;
        }

        item.appendChild(colorBox);
        item.appendChild(label);
        legendContent.appendChild(item);
    }

    // Ajouter "Pas de données"
    const noDataItem = document.createElement('div');
    noDataItem.className = 'legend-item';
    const noDataColor = document.createElement('div');
    noDataColor.className = 'legend-color';
    noDataColor.style.backgroundColor = '#e5e7eb';
    const noDataLabel = document.createElement('span');
    noDataLabel.className = 'text-xs text-gray-700';
    noDataLabel.textContent = 'Pas de données';
    noDataItem.appendChild(noDataColor);
    noDataItem.appendChild(noDataLabel);
    legendContent.appendChild(noDataItem);

    legend.classList.remove('hidden');
}

// ============================================================================
// UTILITAIRES UI
// ============================================================================

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showNoDataMessage() {
    document.getElementById('no-data-message').classList.remove('hidden');
}

function hideNoDataMessage() {
    document.getElementById('no-data-message').classList.add('hidden');
}

function showInfoSidebar() {
    const sidebar = document.getElementById('sidebar-right');
    sidebar.classList.remove('collapsed');
    const icon = document.getElementById('toggle-right').querySelector('i');
    icon.classList.remove('fa-chevron-left');
    icon.classList.add('fa-chevron-right');
}

function hideInfoSidebar() {
    const sidebar = document.getElementById('sidebar-right');
    sidebar.classList.add('collapsed');
    document.getElementById('zone-details').classList.add('hidden');
}

function showError(message) {
    alert(message); // Peut être remplacé par une notification plus élégante
}

function formatNumber(num) {
    if (!num) return '0';
    return new Intl.NumberFormat('fr-FR', {
        maximumFractionDigits: 0
    }).format(num);
}
