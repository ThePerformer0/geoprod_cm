from rest_framework import serializers
from .models import Region, Departement, Arrondissement, Production


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'nom', 'code', 'superficie', 'geom']


class DepartementSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    
    class Meta:
        model = Departement
        fields = ['id', 'nom', 'code', 'region', 'region_nom', 'superficie', 'geom']


class ArrondissementSerializer(serializers.ModelSerializer):
    departement_nom = serializers.CharField(source='departement.nom', read_only=True)
    region_nom = serializers.CharField(source='departement.region.nom', read_only=True)
    
    class Meta:
        model = Arrondissement
        fields = ['id', 'nom', 'code', 'departement', 'departement_nom', 'region_nom', 'superficie', 'geom']


class ProductionSerializer(serializers.ModelSerializer):
    zone_nom = serializers.SerializerMethodField()
    niveau_admin_display = serializers.CharField(source='get_niveau_administratif_display', read_only=True)
    secteur_display = serializers.CharField(source='get_secteur_display', read_only=True)
    
    class Meta:
        model = Production
        fields = [
            'id', 'secteur', 'secteur_display', 'produit', 'annee',
            'niveau_administratif', 'niveau_admin_display',
            'region', 'departement', 'arrondissement',
            'zone_nom', 'quantite', 'unite', 'source_donnee',
            'date_collecte', 'notes'
        ]
    
    def get_zone_nom(self, obj):
        return obj.get_zone()