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

    if (toggleLeft) {
        toggleLeft.addEventListener('click', function () {
            if (sidebarLeft.classList.contains('collapsed')) {
                expandSidebar();
            } else {
                collapseSidebar();
            }
        });
    }

    const icons = sidebarLeft.querySelectorAll('.sidebar-icons .icon-item');
    icons.forEach(icon => {
        icon.addEventListener('click', () => {
            expandSidebar();
        });
    });
}

function collapseSidebar() {
    const sidebarLeft = document.getElementById('sidebar-left');
    const toggleLeft = document.getElementById('toggle-left');
    if (sidebarLeft && !sidebarLeft.classList.contains('collapsed')) {
        sidebarLeft.classList.add('collapsed');
        if (toggleLeft) {
            const icon = toggleLeft.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            }
        }
    }
}

function expandSidebar() {
    const sidebarLeft = document.getElementById('sidebar-left');
    const toggleLeft = document.getElementById('toggle-left');
    if (sidebarLeft && sidebarLeft.classList.contains('collapsed')) {
        sidebarLeft.classList.remove('collapsed');
        if (toggleLeft) {
            const icon = toggleLeft.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }
        }
    }
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
        anneeSelect.innerHTML = '';
        if (data.annees && data.annees.length > 0) {
            data.annees.forEach(annee => {
                const option = document.createElement('option');
                option.value = annee;
                option.textContent = annee;
                anneeSelect.appendChild(option);
            });
            anneeSelect.value = data.annees[0];
            state.filters.annee = data.annees[0];
        } else {
            anneeSelect.innerHTML = '<option value="">— Aucune année —</option>';
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
            resultsContainer.style.display = 'none';
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
        container.style.display = 'none';
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
            container.style.display = 'none';
        });

        container.appendChild(div);
    });

    container.style.display = 'block';
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

        // La sidebar se replie automatiquement quand les données apparaissent
        collapseSidebar();

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
        emptyState.style.display = 'flex';
        updatePaginationUI(0);
        return;
    }

    emptyState.style.display = 'none';

    state.data.results.forEach((row, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="padding:.75rem 1.125rem;font-size:.875rem;color:${row.region_nom ? '#374151' : '#d1d5db'};font-style:${row.region_nom ? 'normal' : 'italic'};">${row.region_nom || '\u2014'}</td>
            <td style="padding:.75rem 1.125rem;font-size:.875rem;color:${row.departement_nom ? '#374151' : '#d1d5db'};font-style:${row.departement_nom ? 'normal' : 'italic'};">${row.departement_nom || '\u2014'}</td>
            <td style="padding:.75rem 1.125rem;font-size:.875rem;color:${row.arrondissement_nom ? '#374151' : '#d1d5db'};font-style:${row.arrondissement_nom ? 'normal' : 'italic'};">${row.arrondissement_nom || '\u2014'}</td>
            <td style="padding:.75rem 1.125rem;font-size:.875rem;font-weight:700;color:#111827;">${row.produit}</td>
            <td style="padding:.75rem 1.125rem;font-size:.875rem;font-weight:700;color:#15803d;font-variant-numeric:tabular-nums;">${formatNum(row.quantite)}</td>
            <td style="padding:.75rem 1.125rem;font-size:.8125rem;color:#9ca3af;font-weight:500;">${row.unite}</td>
            <td style="padding:.75rem 1.125rem;font-size:.875rem;font-weight:600;color:#374151;text-align:center;">${row.annee}</td>
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
    const loadingEl = document.getElementById('table-loading');
    const tbody = document.getElementById('data-table-body');
    loadingEl.style.display = show ? 'flex' : 'none';
    tbody.style.opacity = show ? '0.3' : '1';
}

function formatNum(num) {
    if (!num) return '0';
    return new Intl.NumberFormat('fr-FR').format(num);
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        error:   'fa-circle-xmark',
        success: 'fa-circle-check',
        warning: 'fa-triangle-exclamation',
        info:    'fa-circle-info'
    };
    const colors = {
        error:   { bg: 'rgba(254,242,242,.97)', color: '#991b1b', border: 'rgba(254,202,202,.5)' },
        success: { bg: 'rgba(240,253,244,.97)', color: '#14532d', border: 'rgba(187,247,208,.5)' },
        warning: { bg: 'rgba(255,251,235,.97)', color: '#92400e', border: 'rgba(253,230,138,.5)' },
        info:    { bg: 'rgba(239,246,255,.97)', color: '#1e40af', border: 'rgba(191,219,254,.5)' }
    };

    const c = colors[type] || colors.info;
    const icon = icons[type] || icons.info;

    const toast = document.createElement('div');
    toast.style.cssText = `
        display:flex; align-items:flex-start; gap:.75rem;
        padding:.875rem 1.125rem;
        border-radius:12px;
        box-shadow:0 8px 24px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.06);
        font-family:'Inter',sans-serif; font-size:.875rem; font-weight:500;
        max-width:360px;
        background:${c.bg}; color:${c.color};
        border:1px solid ${c.border};
        backdrop-filter:blur(12px);
        animation:toastSlideIn .35s cubic-bezier(.34,1.56,.64,1) forwards;
    `;

    toast.innerHTML = `
        <i class="fas ${icon}" style="font-size:1rem;flex-shrink:0;margin-top:.05rem;"></i>
        <span style="flex:1;line-height:1.4;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;opacity:.5;padding:0;color:inherit;font-size:.75rem;margin-left:.25rem;flex-shrink:0;">
            <i class="fas fa-xmark"></i>
        </button>
    `;

    if (!document.getElementById('toast-kf')) {
        const s = document.createElement('style');
        s.id = 'toast-kf';
        s.textContent = `@keyframes toastSlideIn{from{opacity:0;transform:translateX(100%) scale(.9)}to{opacity:1;transform:translateX(0) scale(1)}}`;
        document.head.appendChild(s);
    }

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn .3s cubic-bezier(.4,0,.2,1) reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}
