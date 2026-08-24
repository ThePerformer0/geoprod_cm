from django.test import TestCase, Client


class HTMLViewsAndUITest(TestCase):
    """Tests d'integration pour les vues HTML et la conformite de l'interface utilisateur."""

    def setUp(self):
        self.client = Client()

    def test_home_route_accessible(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 301, 302])

    def test_carte_page_renders_with_status_200(self):
        response = self.client.get("/carte/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "carte.html")

    def test_carte_page_has_all_required_js_dom_ids(self):
        content = self.client.get("/carte/").content.decode("utf-8")
        required_ids = [
            "map",
            "filter-form",
            "sidebar-left",
            "sidebar-right",
            "secteur",
            "produit",
            "annee",
            "niveau",
            "loading",
            "no-data-message",
            "legend",
            "toast-container",
            "total-production",
            "zone-dominante",
            "nombre-zones",
            "zone-details",
        ]
        for dom_id in required_ids:
            self.assertIn(f'id="{dom_id}"', content, msg=f"L'element id='{dom_id}' est requis dans carte.html pour le fonctionnement JS")

    def test_carte_page_includes_leaflet_and_inter_font(self):
        content = self.client.get("/carte/").content.decode("utf-8")
        self.assertIn("leaflet", content.lower())
        self.assertIn("Inter", content)

    def test_donnees_page_renders_with_status_200(self):
        response = self.client.get("/donnees/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "donnees.html")

    def test_donnees_page_has_all_required_js_dom_ids(self):
        content = self.client.get("/donnees/").content.decode("utf-8")
        required_ids = [
            "data-table-body",
            "table-empty",
            "table-loading",
            "synth-total",
            "synth-top-zone",
            "synth-count",
            "synth-top-secteur",
            "filter-form",
            "secteur",
            "produit",
            "annee",
            "lieu-search",
            "prev-page",
            "next-page",
            "pagination-info",
            "export-excel",
            "toast-container",
        ]
        for dom_id in required_ids:
            self.assertIn(f'id="{dom_id}"', content, msg=f"L'element id='{dom_id}' est requis dans donnees.html pour le fonctionnement JS")

    def test_donnees_page_active_navigation_state(self):
        content = self.client.get("/donnees/").content.decode("utf-8")
        self.assertIn("nav-pill-active", content)

    def test_static_asset_references_in_templates(self):
        carte_content = self.client.get("/carte/").content.decode("utf-8")
        donnees_content = self.client.get("/donnees/").content.decode("utf-8")

        self.assertIn("carte.css", carte_content)
        self.assertIn("carte.js", carte_content)
        self.assertIn("donnees.css", donnees_content)
        self.assertIn("donnees.js", donnees_content)
