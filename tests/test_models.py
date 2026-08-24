import json
from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from geoprod_cm.models import Region, Departement, Arrondissement, Production
from tests.fixtures import create_test_data


class RegionModelTest(TestCase):
    """Tests unitaires du modele Region."""

    def setUp(self):
        self.data = create_test_data()

    def test_region_attributes(self):
        region = self.data["region_centre"]
        self.assertEqual(region.nom, "Centre")
        self.assertEqual(region.code, "CE")
        self.assertAlmostEqual(region.latitude, 3.87)
        self.assertAlmostEqual(region.longitude, 11.52)
        self.assertEqual(region.superficie, 68926.0)

    def test_region_str(self):
        self.assertEqual(str(self.data["region_centre"]), "Centre")

    def test_region_nom_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Region.objects.create(nom="Centre", code="CE_DOUBLON")

    def test_region_geom_json_is_valid_geojson(self):
        geom = json.loads(self.data["region_centre"].geom_json)
        self.assertEqual(geom["type"], "Polygon")
        self.assertIsInstance(geom["coordinates"], list)

    def test_region_ordering(self):
        regions = list(Region.objects.values_list("nom", flat=True))
        self.assertEqual(regions, sorted(regions))


class DepartementModelTest(TestCase):
    """Tests unitaires du modele Departement."""

    def setUp(self):
        self.data = create_test_data()

    def test_departement_attributes(self):
        dept = self.data["dept_mfoundi"]
        self.assertEqual(dept.nom, "Mfoundi")
        self.assertEqual(dept.code, "MFO")
        self.assertEqual(dept.region, self.data["region_centre"])

    def test_departement_str(self):
        self.assertEqual(str(self.data["dept_mfoundi"]), "Mfoundi (Centre)")

    def test_departement_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            Departement.objects.create(
                nom="Mfoundi",
                region=self.data["region_centre"]
            )

    def test_cascade_delete_on_region(self):
        region_id = self.data["region_centre"].id
        self.data["region_centre"].delete()
        self.assertFalse(Departement.objects.filter(region_id=region_id).exists())


class ArrondissementModelTest(TestCase):
    """Tests unitaires du modele Arrondissement."""

    def setUp(self):
        self.data = create_test_data()

    def test_arrondissement_attributes(self):
        arr = self.data["arr_yde1"]
        self.assertEqual(arr.nom, "Yaounde 1er")
        self.assertEqual(arr.code, "YDE1")
        self.assertEqual(arr.departement, self.data["dept_mfoundi"])

    def test_arrondissement_str(self):
        self.assertEqual(str(self.data["arr_yde1"]), "Yaounde 1er (Mfoundi)")

    def test_cascade_delete_on_departement(self):
        dept_id = self.data["dept_mfoundi"].id
        self.data["dept_mfoundi"].delete()
        self.assertFalse(Arrondissement.objects.filter(departement_id=dept_id).exists())


class ProductionModelTest(TestCase):
    """Tests unitaires du modele Production."""

    def setUp(self):
        self.data = create_test_data()

    def test_production_creation(self):
        prod = self.data["prod1"]
        self.assertEqual(prod.secteur, "agriculture")
        self.assertEqual(prod.produit, "Cacao")
        self.assertEqual(prod.annee, 2022)
        self.assertEqual(prod.quantite, Decimal("85000.00"))
        self.assertEqual(prod.unite, "tonnes")

    def test_production_str(self):
        prod_str = str(self.data["prod1"])
        self.assertIn("Cacao", prod_str)
        self.assertIn("Centre", prod_str)
        self.assertIn("2022", prod_str)

    def test_get_zone_for_region(self):
        self.assertEqual(self.data["prod1"].get_zone(), "Centre")

    def test_get_zone_for_departement(self):
        self.assertEqual(self.data["prod4"].get_zone(), "Mfoundi")

    def test_get_zone_for_arrondissement(self):
        self.assertEqual(self.data["prod5"].get_zone(), "Yaounde 1er")

    def test_get_zone_id_for_region(self):
        self.assertEqual(self.data["prod1"].get_zone_id(), self.data["region_centre"].id)

    def test_get_zone_id_for_departement(self):
        self.assertEqual(self.data["prod4"].get_zone_id(), self.data["dept_mfoundi"].id)

    def test_get_zone_id_for_arrondissement(self):
        self.assertEqual(self.data["prod5"].get_zone_id(), self.data["arr_yde1"].id)

    def test_secteur_choices_validity(self):
        valid_secteurs = {c[0] for c in Production.SECTEUR_CHOICES}
        self.assertEqual(valid_secteurs, {"agriculture", "elevage", "peche"})

    def test_cascade_delete_on_region_deletes_production(self):
        region_id = self.data["region_centre"].id
        self.data["region_centre"].delete()
        self.assertFalse(Production.objects.filter(region_id=region_id).exists())
