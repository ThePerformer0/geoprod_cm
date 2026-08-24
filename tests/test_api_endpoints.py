from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from tests.fixtures import create_test_data


class RegionAPITest(TestCase):
    """Tests d'integration pour l'API /api/regions/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def _get_results(self, response_json):
        if isinstance(response_json, list):
            return response_json
        return response_json.get("results", [])

    def test_list_regions_returns_200(self):
        response = self.client.get("/api/regions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_regions_count(self):
        response = self.client.get("/api/regions/")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 3)

    def test_retrieve_single_region(self):
        pk = self.data["region_centre"].id
        response = self.client.get(f"/api/regions/{pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["nom"], "Centre")
        self.assertEqual(data["code"], "CE")
        self.assertIn("geom_json", data)

    def test_retrieve_nonexistent_region_returns_404(self):
        response = self.client.get("/api/regions/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_region_by_nom(self):
        response = self.client.get("/api/regions/?search=Sud")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nom"], "Sud")

    def test_region_productions_custom_action(self):
        pk = self.data["region_centre"].id
        response = self.client.get(f"/api/regions/{pk}/productions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["produit"], "Cacao")


class DepartementAPITest(TestCase):
    """Tests d'integration pour l'API /api/departements/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def _get_results(self, response_json):
        if isinstance(response_json, list):
            return response_json
        return response_json.get("results", [])

    def test_list_departements_returns_200(self):
        response = self.client.get("/api/departements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_departement_includes_region_nom(self):
        pk = self.data["dept_mfoundi"].id
        response = self.client.get(f"/api/departements/{pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["nom"], "Mfoundi")
        self.assertEqual(data["region_nom"], "Centre")

    def test_filter_departements_by_region(self):
        region_id = self.data["region_centre"].id
        response = self.client.get(f"/api/departements/?region={region_id}")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nom"], "Mfoundi")


class ArrondissementAPITest(TestCase):
    """Tests d'integration pour l'API /api/arrondissements/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def _get_results(self, response_json):
        if isinstance(response_json, list):
            return response_json
        return response_json.get("results", [])

    def test_list_arrondissements_returns_200(self):
        response = self.client.get("/api/arrondissements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_arrondissement_includes_hierarchy(self):
        pk = self.data["arr_yde1"].id
        response = self.client.get(f"/api/arrondissements/{pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["nom"], "Yaounde 1er")
        self.assertEqual(data["departement_nom"], "Mfoundi")
        self.assertEqual(data["region_nom"], "Centre")


class ProductionAPITest(TestCase):
    """Tests d'integration pour l'API /api/productions/."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def _get_results(self, response_json):
        if isinstance(response_json, dict):
            return response_json.get("results", [])
        return response_json

    def test_list_productions_returns_200(self):
        response = self.client.get("/api/productions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_secteur(self):
        response = self.client.get("/api/productions/?secteur=agriculture")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["secteur"], "agriculture")

    def test_filter_by_produit(self):
        response = self.client.get("/api/productions/?produit=Cacao")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["produit"], "Cacao")

    def test_filter_by_annee(self):
        response = self.client.get("/api/productions/?annee=2023")
        results = self._get_results(response.json())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["produit"], "Bovins")

    def test_ordering_by_quantite_desc(self):
        response = self.client.get("/api/productions/?ordering=-quantite")
        results = self._get_results(response.json())
        quantites = [float(r["quantite"]) for r in results]
        self.assertEqual(quantites, sorted(quantites, reverse=True))

    def test_production_serializer_computed_fields(self):
        pk = self.data["prod1"].id
        response = self.client.get(f"/api/productions/{pk}/")
        data = response.json()
        self.assertEqual(data["zone_nom"], "Centre")
        self.assertEqual(data["secteur_display"], "Agriculture")
        self.assertEqual(data["niveau_admin_display"], "Région")
