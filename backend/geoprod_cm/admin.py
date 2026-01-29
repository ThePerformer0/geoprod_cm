from django.contrib import admin
from .models import Region, Departement, Arrondissement, Production


class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'code', 'superficie', 'created_at')
    search_fields = ('nom', 'code')
    list_filter = ('created_at',)
    ordering = ('nom',)


class DepartementAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'code', 'region', 'superficie', 'created_at')
    search_fields = ('nom', 'code', 'region__nom')
    list_filter = ('region', 'created_at')
    ordering = ('nom',)
    raw_id_fields = ('region',)


class ArrondissementAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'code', 'departement', 'region_nom', 'superficie', 'created_at')
    search_fields = ('nom', 'code', 'departement__nom')
    list_filter = ('departement__region', 'created_at')
    ordering = ('nom',)
    raw_id_fields = ('departement',)
    
    def region_nom(self, obj):
        return obj.departement.region.nom if obj.departement and obj.departement.region else ''
    region_nom.short_description = 'Région'
    region_nom.admin_order_field = 'departement__region__nom'


class ProductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'secteur_display', 'annee', 'zone_nom', 'quantite', 'unite', 'source_donnee')
    list_filter = ('secteur', 'annee', 'niveau_administratif')
    search_fields = ('produit', 'region__nom', 'departement__nom', 'arrondissement__nom')
    ordering = ('-annee', 'produit')
    raw_id_fields = ('region', 'departement', 'arrondissement')
    date_hierarchy = 'date_collecte'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('secteur', 'produit', 'annee', 'niveau_administratif')
        }),
        ('Localisation', {
            'fields': ('region', 'departement', 'arrondissement')
        }),
        ('Données de production', {
            'fields': ('quantite', 'unite', 'source_donnee', 'date_collecte')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def secteur_display(self, obj):
        return obj.get_secteur_display()
    secteur_display.short_description = 'Secteur'
    
    def zone_nom(self, obj):
        return obj.get_zone()
    zone_nom.short_description = 'Zone'


# Enregistrement des modèles dans l'admin
admin.site.register(Region, RegionAdmin)
admin.site.register(Departement, DepartementAdmin)
admin.site.register(Arrondissement, ArrondissementAdmin)
admin.site.register(Production, ProductionAdmin)