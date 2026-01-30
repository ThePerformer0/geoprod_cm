// ============================================================================
// ANALYSE DES DONNÉES - BASSINS DE PRODUCTION CAMEROUN
// ============================================================================

// Configuration globale
const API_BASE_URL = '/api/productions';

// Listes prédéfinies de produits par secteur
const PRODUITS_PAR_SECTEUR = {
    agriculture: [
        'Maïs', 'Riz', 'Manioc', 'Banane plantain', 'Cacao', 'Café', 'Coton',
        'Arachide', 'Sorgho', 'Mil', 'Igname', 'Macabo', 'Haricot', 'Tomate', 'Oignon'
    ],
    elevage: [
        'Bovins', 'Ovins', 'Caprins', 'Porcins'
    ],
    peche: [
        'Pêche maritime', 'Pêche en eau douce', 'Pêche lacustre',
        'Pêche fluviale', 'Tilapia', 'Silure', 'Carpe', 'Crevettes'
    ]
};

// État de l'application
let state = {
    currentPage: 1,
    pageSize: 20,
    filters: {
        secteur: 'agriculture',
        produit: 'Cacao',
        annee: '',
        region: '',
        departement: '',
        arrondissement: '',
        lieu_search: ''
    },
    data: { results: [], count: 0, next: null, previous: null },
    stats: null
};

// ============================================================================
// INITIALISATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initFilterOptions().then(() => {
        setDefaultFilters();
        updateAnalysis();
    });
    setupEventListeners();
});

// ============================================================================
// GESTION DU SIDEBAR
// ============================================================================

function initSidebar() {
    const toggleLeft = document.getElementById('toggle-left');
    const sidebarLeft = document.getElementById('sidebar-left');
    const mainContent = document.querySelector('main');

    toggleLeft.addEventListener('click', function () {
        sidebarLeft.classList.toggle('collapsed');
        const icon = toggleLeft.querySelector('i');
        icon.classList.toggle('fa-chevron-left');
        icon.classList.toggle('fa-chevron-right');

        if (sidebarLeft.classList.contains('collapsed')) {
            mainContent.classList.add('px-16');
        } else {
            mainContent.classList.remove('px-16');
        }
    });

    const icons = sidebarLeft.querySelectorAll('.sidebar-icons .icon-item');
    icons.forEach(icon => {
        icon.addEventListener('click', () => {
            if (sidebarLeft.classList.contains('collapsed')) {
                toggleLeft.click();
            }
        });
    });
}

// ============================================================================
// FILTRES ET AUTOCOMPLÉTION
// ============================================================================

async function initFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/filtres/`);
        const data = await response.json();

        // Remplir les années
        const anneeSelect = document.getElementById('annee');
        data.annees.forEach(annee => {
            const option = document.createElement('option');
            option.value = annee;
            option.textContent = annee;
            anneeSelect.appendChild(option);
        });

        if (data.annees.length > 0) {
            anneeSelect.value = data.annees[0];
            state.filters.annee = data.annees[0];
        }

    } catch (error) {
        console.error('Erreur initialisation filtres:', error);
    }
}

function setDefaultFilters() {
    document.getElementById('secteur').value = 'agriculture';
    updateProductList('agriculture');
    document.getElementById('produit').value = 'Cacao';
}

function updateProductList(secteur) {
    const produitSelect = document.getElementById('produit');
    const produits = PRODUITS_PAR_SECTEUR[secteur] || [];

    produitSelect.innerHTML = '<option value="">-- Tous les produits --</option>';
    produits.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p; opt.textContent = p;
        produitSelect.appendChild(opt);
    });
    produitSelect.disabled = false;
}

function setupEventListeners() {
    document.getElementById('secteur').addEventListener('change', function () {
        updateProductList(this.value);
    });

    const lieuInput = document.getElementById('lieu-search');
    const resultsContainer = document.getElementById('autocomplete-results');
    let debounceTimer;

    lieuInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            resultsContainer.classList.add('hidden');
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/autocomplete/?q=${query}`);
                const results = await response.json();
                displayAutocompleteResults(results);
            } catch (err) {
                console.error('Erreur autocomplete:', err);
            }
        }, 300);
    });

    document.getElementById('filter-form').addEventListener('submit', (e) => {
        e.preventDefault();
        state.currentPage = 1;
        updateAnalysis();
    });

    document.getElementById('reset-filters').addEventListener('click', () => {
        document.getElementById('filter-form').reset();
        document.getElementById('lieu-id').value = '';
        document.getElementById('lieu-type').value = '';
        setDefaultFilters();
        updateAnalysis();
    });

    document.getElementById('prev-page').addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            updateAnalysis();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        if (state.data.next) {
            state.currentPage++;
            updateAnalysis();
        }
    });

    document.getElementById('export-excel').addEventListener('click', () => {
        const params = buildQueryParams();
        window.location.href = `${API_BASE_URL}/export_excel/?${params.toString()}`;
    });
}

function displayAutocompleteResults(results) {
    const container = document.getElementById('autocomplete-results');
    container.innerHTML = '';

    if (results.length === 0) {
        container.classList.add('hidden');
        return;
    }

    results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'result-item flex items-center';

        const typeClass = `type-${item.type}`;
        div.innerHTML = `
            <span class="result-type ${typeClass}">${item.type}</span>
            <div>
                <div class="font-bold text-gray-800">${item.nom}</div>
                <div class="text-xs text-gray-500">${item.hierarchie}</div>
            </div>
        `;

        div.addEventListener('click', () => {
            document.getElementById('lieu-search').value = item.nom;
            document.getElementById('lieu-id').value = item.id;
            document.getElementById('lieu-type').value = item.type;
            container.classList.add('hidden');
        });

        container.appendChild(div);
    });

    container.classList.remove('hidden');
}

// ============================================================================
// DATA FETCHING & UPDATE
// ============================================================================

async function updateAnalysis() {
    showTableLoading(true);

    try {
        const params = buildQueryParams();

        // Parallel requests for table and stats
        const [dataRes, statsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/?${params.toString()}&page=${state.currentPage}&page_size=${state.pageSize}`),
            fetch(`${API_BASE_URL}/statistiques/?${params.toString()}`)
        ]);

        const dataJson = await dataRes.json();
        const statsJson = await statsRes.json();

        state.data = dataJson;
        state.stats = statsJson;

        updateDataTable();
        updateSynthesis();
        updatePageInfo();

    } catch (err) {
        console.error('Erreur chargement données:', err);
    } finally {
        showTableLoading(false);
    }
}

function buildQueryParams() {
    const params = new URLSearchParams();

    const secteur = document.getElementById('secteur').value;
    const produit = document.getElementById('produit').value;
    const annee = document.getElementById('annee').value;
    const lieuId = document.getElementById('lieu-id').value;
    const lieuType = document.getElementById('lieu-type').value;

    if (secteur) params.append('secteur', secteur);
    if (produit) params.append('produit', produit);
    if (annee) params.append('annee', annee);

    if (lieuId && lieuType) {
        if (lieuType === 'region') params.append('region', lieuId);
        if (lieuType === 'departement') params.append('departement', lieuId);
        if (lieuType === 'arrondissement') params.append('arrondissement', lieuId);
    }

    return params;
}

function updatePageInfo() {
    const produit = document.getElementById('produit').value || 'Tous produits';
    const lieu = document.getElementById('lieu-search').value || 'Cameroun';
    const annee = document.getElementById('annee').value || 'Toutes années';

    document.getElementById('page-title').textContent = `${produit} - ${lieu}`;
    document.getElementById('page-subtitle').textContent = `Synthèse des données SIG • Année ${annee}`;
}

// ============================================================================
// SYNTHESIS UPDATE (Cards)
// ============================================================================

function updateSynthesis() {
    if (!state.stats) return;

    const stats = state.stats;
    const unite = state.data.results.length > 0 ? state.data.results[0].unite : '';

    // Total Production
    document.getElementById('synth-total').textContent = `${formatNum(stats.total_quantite)} ${unite}`;

    // Top Zone
    const topZone = stats.top_produits && stats.top_produits.length > 0 ? stats.top_produits[0].produit : '-';
    // Actually top_produits is by product name, let's look at the API again.
    // In many cases we'd want top region/dept. Let's use what we have or just simplify.
    document.getElementById('synth-top-zone').textContent = stats.zone_dominante || 'N/A';

    // Count
    document.getElementById('synth-count').textContent = formatNum(state.data.count);

    // Top Secteur
    if (stats.par_secteur && stats.par_secteur.length > 0) {
        const topSect = stats.par_secteur.sort((a, b) => b.count - a.count)[0];
        document.getElementById('synth-top-secteur').textContent =
            topSect.secteur.charAt(0).toUpperCase() + topSect.secteur.slice(1);
    } else {
        document.getElementById('synth-top-secteur').textContent = '-';
    }
}

// ============================================================================
// TABLE UPDATE
// ============================================================================

function updateDataTable() {
    const tbody = document.getElementById('data-table-body');
    const emptyState = document.getElementById('table-empty');

    tbody.innerHTML = '';

    if (!state.data.results || state.data.results.length === 0) {
        emptyState.classList.remove('hidden');
        updatePaginationUI(0);
        return;
    }

    emptyState.classList.add('hidden');

    state.data.results.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition';
        tr.innerHTML = `
            <td class="px-6 py-4 text-sm text-gray-500 font-medium italic">${row.region_nom || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-500 italic">${row.departement_nom || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-500 italic">${row.arrondissement_nom || '-'}</td>
            <td class="px-6 py-4 text-sm font-bold text-gray-700">${row.produit}</td>
            <td class="px-6 py-4 text-sm font-bold text-green-600">${formatNum(row.quantite)}</td>
            <td class="px-6 py-4 text-sm text-gray-400 font-medium">${row.unite}</td>
            <td class="px-6 py-4 text-sm text-gray-600 text-center font-bold">${row.annee}</td>
        `;
        tbody.appendChild(tr);
    });

    updatePaginationUI(state.data.count);
}

function updatePaginationUI(totalCount) {
    const info = document.getElementById('pagination-info');
    const start = totalCount > 0 ? (state.currentPage - 1) * state.pageSize + 1 : 0;
    const end = Math.min(state.currentPage * state.pageSize, totalCount);

    info.textContent = `Affichage de ${start} à ${end} sur ${totalCount} résultats`;

    document.getElementById('prev-page').disabled = state.currentPage === 1;
    document.getElementById('next-page').disabled = !state.data.next;
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showTableLoading(show) {
    document.getElementById('table-loading').classList.toggle('hidden', !show);
    document.getElementById('data-table-body').classList.toggle('opacity-30', show);
}

function formatNum(num) {
    if (!num) return '0';
    return new Intl.NumberFormat('fr-FR').format(num);
}
