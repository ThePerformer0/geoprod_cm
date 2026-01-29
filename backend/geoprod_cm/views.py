from itertools import count
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Max, Min
from .models import Region, Departement, Arrondissement, Production
from .serializers import (
    RegionSerializer, DepartementSerializer, 
    ArrondissementSerializer, ProductionSerializer
)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all().order_by('nom')
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'code']
    
    @action(detail=True, methods=['get'])
    def productions(self, request, pk=None):
        """Récupère toutes les productions d'une région"""
        region = self.get_object()
        productions = Production.objects.filter(region=region)
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)


class DepartementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Departement.objects.all().order_by('nom')
    serializer_class = DepartementSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nom', 'code']
    filterset_fields = ['region']
    
    @action(detail=True, methods=['get'])
    def productions(self, request, pk=None):
        """Récupère toutes les productions d'un département"""
        departement = self.get_object()
        productions = Production.objects.filter(departement=departement)
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)


class ArrondissementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Arrondissement.objects.all().order_by('nom')
    serializer_class = ArrondissementSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nom', 'code']
    filterset_fields = ['departement', 'departement__region']


class ProductionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Production.objects.all().order_by('-annee', 'produit')
    serializer_class = ProductionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['produit', 'region__nom', 'departement__nom', 'arrondissement__nom']
    filterset_fields = ['secteur', 'annee', 'niveau_administratif', 'region', 'departement']
    ordering_fields = ['annee', 'quantite', 'produit']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Retourne des statistiques globales sur les productions"""
        # Aggrégations
        total_productions = Production.objects.count()
        total_quantite = Production.objects.aggregate(total=Sum('quantite'))['total'] or 0
        
        # Par secteur
        par_secteur = Production.objects.values('secteur').annotate(
            count=Sum('quantite'),
            nombre=count('id')
        )
        
        # Par année
        par_annee = Production.objects.values('annee').annotate(
            total=Sum('quantite')
        ).order_by('-annee')[:5]
        
        # Top 10 produits
        top_produits = Production.objects.values('produit').annotate(
            total=Sum('quantite')
        ).order_by('-total')[:10]
        
        return Response({
            'total_productions': total_productions,
            'total_quantite': float(total_quantite),
            'par_secteur': list(par_secteur),
            'par_annee': list(par_annee),
            'top_produits': list(top_produits),
        })
    
    @action(detail=False, methods=['get'])
    def filtres(self, request):
        """Retourne les valeurs disponibles pour les filtres"""
        secteurs = Production.SECTEUR_CHOICES
        annees = Production.objects.values_list('annee', flat=True).distinct().order_by('-annee')
        produits = Production.objects.values_list('produit', flat=True).distinct().order_by('produit')
        
        return Response({
            'secteurs': [{'value': s[0], 'label': s[1]} for s in secteurs],
            'annees': list(annees),
            'produits': list(produits),
        })