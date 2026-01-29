import json
from rest_framework import serializers
from .models import Region, Departement, Arrondissement, Production


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = [
            'id', 'nom', 'code', 'latitude', 'longitude', 
            'geom_json', 'superficie', 'created_at'
        ]
        read_only_fields = ['created_at']


class DepartementSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    region_code = serializers.CharField(source='region.code', read_only=True)
    
    class Meta:
        model = Departement
        fields = [
            'id', 'nom', 'code', 'region', 'region_nom', 'region_code',
            'latitude', 'longitude', 'geom_json', 'superficie', 'created_at'
        ]
        read_only_fields = ['created_at']


class ArrondissementSerializer(serializers.ModelSerializer):
    departement_nom = serializers.CharField(source='departement.nom', read_only=True)
    region_nom = serializers.CharField(source='departement.region.nom', read_only=True)
    region_code = serializers.CharField(source='departement.region.code', read_only=True)
    
    class Meta:
        model = Arrondissement
        fields = [
            'id', 'nom', 'code', 'departement', 'departement_nom',
            'region_nom', 'region_code', 'latitude', 'longitude',
            'geom_json', 'superficie', 'created_at'
        ]
        read_only_fields = ['created_at']


class ProductionSerializer(serializers.ModelSerializer):
    zone_nom = serializers.SerializerMethodField()
    niveau_admin_display = serializers.CharField(source='get_niveau_administratif_display', read_only=True)
    secteur_display = serializers.CharField(source='get_secteur_display', read_only=True)
    region_nom = serializers.CharField(source='region.nom', read_only=True, allow_null=True)
    departement_nom = serializers.CharField(source='departement.nom', read_only=True, allow_null=True)
    arrondissement_nom = serializers.CharField(source='arrondissement.nom', read_only=True, allow_null=True)
    
    class Meta:
        model = Production
        fields = [
            'id', 'secteur', 'secteur_display', 'produit', 'annee',
            'niveau_administratif', 'niveau_admin_display',
            'region', 'region_nom', 'departement', 'departement_nom',
            'arrondissement', 'arrondissement_nom', 'zone_nom',
            'quantite', 'unite', 'source_donnee', 'date_collecte',
            'notes', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_zone_nom(self, obj):
        return obj.get_zone()


class GeoJSONFeatureSerializer(serializers.Serializer):
    """Serializer pour une feature GeoJSON avec données de production"""
    type = serializers.CharField(default='Feature')
    id = serializers.IntegerField()
    properties = serializers.DictField()
    geometry = serializers.DictField()


class MapDataSerializer(serializers.Serializer):
    """Serializer pour les données cartographiques (GeoJSON FeatureCollection)"""
    type = serializers.CharField(default='FeatureCollection')
    features = GeoJSONFeatureSerializer(many=True)
    metadata = serializers.DictField()


class AutocompleteSerializer(serializers.Serializer):
    """Serializer pour l'autocomplétion des lieux"""
    id = serializers.IntegerField()
    nom = serializers.CharField()
    type = serializers.CharField()  # 'region', 'departement', 'arrondissement'
    hierarchie = serializers.CharField()  # Ex: "Centre > Mfoundi > Yaoundé"
    niveau_administratif = serializers.CharField()