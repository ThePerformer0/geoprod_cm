import json
from decimal import Decimal
from geoprod_cm.models import Region, Departement, Arrondissement, Production


def create_test_data():
    """
    Cree un jeu de donnees de test complet et coherent pour les tests unitaires et d'integration.
    """
    # 1. Regions
    region_centre = Region.objects.create(
        nom="Centre",
        code="CE",
        latitude=3.87,
        longitude=11.52,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[11.0, 3.0], [12.0, 3.0], [12.0, 4.0], [11.0, 4.0], [11.0, 3.0]]]
        }),
        superficie=68926.0,
    )

    region_sud = Region.objects.create(
        nom="Sud",
        code="SU",
        latitude=2.9,
        longitude=12.3,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[12.0, 2.0], [13.0, 2.0], [13.0, 3.0], [12.0, 3.0], [12.0, 2.0]]]
        }),
        superficie=47110.0,
    )

    region_ouest = Region.objects.create(
        nom="Ouest",
        code="OU",
        latitude=5.48,
        longitude=10.42,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[10.0, 5.0], [11.0, 5.0], [11.0, 6.0], [10.0, 6.0], [10.0, 5.0]]]
        }),
        superficie=13892.0,
    )

    # 2. Departements
    dept_mfoundi = Departement.objects.create(
        nom="Mfoundi",
        code="MFO",
        region=region_centre,
        latitude=3.87,
        longitude=11.52,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[11.4, 3.7], [11.6, 3.7], [11.6, 3.9], [11.4, 3.9], [11.4, 3.7]]]
        }),
        superficie=297.0,
    )

    dept_mvila = Departement.objects.create(
        nom="Mvila",
        code="MVL",
        region=region_sud,
        latitude=2.92,
        longitude=11.15,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[11.0, 2.8], [11.3, 2.8], [11.3, 3.1], [11.0, 3.1], [11.0, 2.8]]]
        }),
        superficie=8697.0,
    )

    # 3. Arrondissements
    arr_yde1 = Arrondissement.objects.create(
        nom="Yaounde 1er",
        code="YDE1",
        departement=dept_mfoundi,
        latitude=3.89,
        longitude=11.51,
        geom_json=json.dumps({
            "type": "Polygon",
            "coordinates": [[[11.48, 3.86], [11.54, 3.86], [11.54, 3.92], [11.48, 3.92], [11.48, 3.86]]]
        }),
    )

    arr_ebolowa1 = Arrondissement.objects.create(
        nom="Ebolowa 1er",
        code="EBW1",
        departement=dept_mvila,
        latitude=2.93,
        longitude=11.16,
    )

    # 4. Productions
    prod1 = Production.objects.create(
        secteur="agriculture",
        produit="Cacao",
        annee=2022,
        niveau_administratif="region",
        region=region_centre,
        quantite=Decimal("85000.00"),
        unite="tonnes",
        source_donnee="MINADER 2022",
    )

    prod2 = Production.objects.create(
        secteur="agriculture",
        produit="Cacao",
        annee=2022,
        niveau_administratif="region",
        region=region_sud,
        quantite=Decimal("45000.00"),
        unite="tonnes",
        source_donnee="MINADER 2022",
    )

    prod3 = Production.objects.create(
        secteur="agriculture",
        produit="Cafe",
        annee=2022,
        niveau_administratif="region",
        region=region_ouest,
        quantite=Decimal("18000.00"),
        unite="tonnes",
        source_donnee="MINADER 2022",
    )

    prod4 = Production.objects.create(
        secteur="elevage",
        produit="Bovins",
        annee=2023,
        niveau_administratif="departement",
        departement=dept_mfoundi,
        quantite=Decimal("6200.00"),
        unite="tetes",
        source_donnee="MINEPIA 2023",
    )

    prod5 = Production.objects.create(
        secteur="peche",
        produit="Tilapia",
        annee=2022,
        niveau_administratif="arrondissement",
        arrondissement=arr_yde1,
        quantite=Decimal("1500.50"),
        unite="tonnes",
        source_donnee="MINEPIA 2022",
    )

    return {
        "region_centre": region_centre,
        "region_sud": region_sud,
        "region_ouest": region_ouest,
        "dept_mfoundi": dept_mfoundi,
        "dept_mvila": dept_mvila,
        "arr_yde1": arr_yde1,
        "arr_ebolowa1": arr_ebolowa1,
        "prod1": prod1,
        "prod2": prod2,
        "prod3": prod3,
        "prod4": prod4,
        "prod5": prod5,
    }
