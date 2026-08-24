from django.test import TestCase
from django.db.models import Sum
from rest_framework.test import APIClient
from geoprod_cm.models import Region, Production
from tests.fixtures import create_test_data


class APIDataConsistencyTest(TestCase):
    """Tests de coherence stricte entre la base de donnees et les reponses de l'API."""

    def setUp(self):
        self.client = APIClient()
        self.data = create_test_data()

    def test_production_total_count_matches_db(self):
        response = self.client.get("/api/productions/")
        data = response.json()
        count = data.get("count", len(data.get("results", data))) if isinstance(data, dict) else len(data)
        self.assertEqual(count, Production.objects.count())

    def test_region_count_matches_db(self):
        response = self.client.get("/api/regions/")
        data = response.json()
        count = data.get("count", len(data.get("results", data))) if isinstance(data, dict) else len(data)
        self.assertEqual(count, Region.objects.count())

    def test_statistiques_agriculture_sum_matches_db_aggregate(self):
        db_sum = float(
            Production.objects.filter(secteur="agriculture").aggregate(total=Sum("quantite"))["total"] or 0
        )
        response = self.client.get("/api/productions/statistiques/?secteur=agriculture")
        api_sum = response.json()["total_quantite"]
        self.assertAlmostEqual(api_sum, db_sum, places=1)

    def test_filtres_annees_exact_match_with_database(self):
        db_years = set(Production.objects.values_list("annee", flat=True).distinct())
        api_years = set(self.client.get("/api/productions/filtres/").json()["annees"])
        self.assertEqual(db_years, api_years)

    def test_map_data_quantite_exact_match_with_database(self):
        response = self.client.get("/api/productions/map_data/?secteur=agriculture&produit=Cacao&annee=2022&niveau=region")
        features = response.json()["features"]
        centre_feature = next((f for f in features if f["properties"]["nom"] == "Centre"), None)
        self.assertIsNotNone(centre_feature)

        db_centre_cacao = float(
            Production.objects.filter(
                secteur="agriculture",
                produit="Cacao",
                annee=2022,
                region__nom="Centre"
            ).aggregate(total=Sum("quantite"))["total"] or 0
        )
        self.assertAlmostEqual(centre_feature["properties"]["quantite"], db_centre_cacao, places=1)
