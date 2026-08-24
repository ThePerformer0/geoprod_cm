from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from geoprod_cm.models import Region
from tests.fixtures import create_test_data


class FiltresEndpointTest(TestCase):
    """Tests pour l'endpoint /api/productions/filtres/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_filtres_status_and_keys(self):
        response = self.client.get("/api/productions/filtres/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("secteurs", data)
        self.assertIn("annees", data)
        self.assertIn("produits", data)

    def test_filtres_secteurs_options(self):
        response = self.client.get("/api/productions/filtres/")
        data = response.json()
        values = [s["value"] for s in data["secteurs"]]
        self.assertIn("agriculture", values)
        self.assertIn("elevage", values)
        self.assertIn("peche", values)

    def test_filtres_annees_descending(self):
        response = self.client.get("/api/productions/filtres/")
        annees = response.json()["annees"]
        self.assertEqual(annees, sorted(annees, reverse=True))


class StatistiquesEndpointTest(TestCase):
    """Tests pour l'endpoint /api/productions/statistiques/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_statistiques_globales(self):
        response = self.client.get("/api/productions/statistiques/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["total_productions"], 5)
        # 85000 + 45000 + 18000 + 6200 + 1500.5 = 155700.5
        self.assertAlmostEqual(data["total_quantite"], 155700.5, places=1)
        self.assertIn("par_secteur", data)
        self.assertIn("zone_dominante", data)

    def test_statistiques_filtrees_secteur(self):
        response = self.client.get("/api/productions/statistiques/?secteur=agriculture")
        data = response.json()
        self.assertEqual(data["total_productions"], 3)
        self.assertAlmostEqual(data["total_quantite"], 148000.0, places=1)
        self.assertEqual(data["zone_dominante"], "Centre")


class MapDataEndpointTest(TestCase):
    """Tests pour l'endpoint /api/productions/map_data/ (GeoJSON)."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_map_data_returns_geojson_feature_collection(self):
        url = "/api/productions/map_data/?secteur=agriculture&produit=Cacao&annee=2022&niveau=region"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertIsInstance(data["features"], list)
        self.assertIn("metadata", data)

    def test_map_data_features_properties(self):
        url = "/api/productions/map_data/?secteur=agriculture&produit=Cacao&annee=2022&niveau=region"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data["features"]), 2)
        for feature in data["features"]:
            self.assertEqual(feature["type"], "Feature")
            props = feature["properties"]
            self.assertIn("nom", props)
            self.assertIn("quantite", props)
            self.assertIn("unite", props)

    def test_map_data_metadata_aggregation(self):
        url = "/api/productions/map_data/?secteur=agriculture&produit=Cacao&annee=2022&niveau=region"
        response = self.client.get(url)
        meta = response.json()["metadata"]
        # Centre: 85000, Sud: 45000 -> Total: 130000
        self.assertAlmostEqual(meta["total_production"], 130000.0, places=1)
        self.assertEqual(meta["zone_dominante"], "Centre")
        self.assertEqual(meta["nombre_zones"], 2)


class AutocompleteEndpointTest(TestCase):
    """Tests pour l'endpoint /api/productions/autocomplete/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_autocomplete_under_2_chars_returns_empty(self):
        response = self.client.get("/api/productions/autocomplete/?q=C")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_autocomplete_search_region(self):
        response = self.client.get("/api/productions/autocomplete/?q=Cent")
        results = response.json()
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["nom"], "Centre")
        self.assertEqual(results[0]["type"], "region")

    def test_autocomplete_search_departement_with_hierarchy(self):
        response = self.client.get("/api/productions/autocomplete/?q=Mfou")
        results = response.json()
        self.assertGreater(len(results), 0)
        item = results[0]
        self.assertEqual(item["nom"], "Mfoundi")
        self.assertEqual(item["type"], "departement")
        self.assertIn("Centre", item["hierarchie"])


class ExportExcelEndpointTest(TestCase):
    """Tests pour l'endpoint /api/productions/export_excel/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_export_excel_headers_and_status(self):
        response = self.client.get("/api/productions/export_excel/?secteur=agriculture")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("spreadsheetml", response["Content-Type"])
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".xlsx", response["Content-Disposition"])
        self.assertGreater(len(response.content), 0)
