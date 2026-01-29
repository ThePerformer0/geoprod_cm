from django.db import models

class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    # Pour stocker les coordonnées simples (centre de la région)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Pour stocker les géométries en JSON (GeoJSON)
    geom_json = models.TextField(null=True, blank=True, verbose_name="Géométrie (JSON)")
    superficie = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Departement(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='departements')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    geom_json = models.TextField(null=True, blank=True, verbose_name="Géométrie (JSON)")
    superficie = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['nom']
        unique_together = ['nom', 'region']
    
    def __str__(self):
        return f"{self.nom} ({self.region.nom})"


class Arrondissement(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='arrondissements')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    geom_json = models.TextField(null=True, blank=True, verbose_name="Géométrie (JSON)")
    superficie = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Arrondissement"
        verbose_name_plural = "Arrondissements"
        ordering = ['nom']
        unique_together = ['nom', 'departement']
    
    def __str__(self):
        return f"{self.nom} ({self.departement.nom})"


class Production(models.Model):
    """Modèle central pour les données de production"""
    
    SECTEUR_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('elevage', 'Élevage'),
        ('peche', 'Pêche'),
    ]
    
    NIVEAU_ADMIN_CHOICES = [
        ('region', 'Région'),
        ('departement', 'Département'),
        ('arrondissement', 'Arrondissement'),
    ]
    
    id = models.AutoField(primary_key=True)
    secteur = models.CharField(max_length=20, choices=SECTEUR_CHOICES)
    produit = models.CharField(max_length=100)
    annee = models.IntegerField()
    niveau_administratif = models.CharField(max_length=20, choices=NIVEAU_ADMIN_CHOICES)
    
    # Clés étrangères vers les différents niveaux administratifs
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, related_name='productions')
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True, blank=True, related_name='productions')
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.CASCADE, null=True, blank=True, related_name='productions')
    
    quantite = models.DecimalField(max_digits=15, decimal_places=2)
    unite = models.CharField(max_length=20)
    source_donnee = models.CharField(max_length=200)
    date_collecte = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Production"
        verbose_name_plural = "Productions"
        ordering = ['-annee', 'secteur', 'produit']
        indexes = [
            models.Index(fields=['secteur']),
            models.Index(fields=['produit']),
            models.Index(fields=['annee']),
            models.Index(fields=['niveau_administratif']),
        ]
    
    def __str__(self):
        zone = self.get_zone()
        return f"{self.produit} - {zone} - {self.annee}"
    
    def get_zone(self):
        """Retourne la zone administrative correspondante"""
        if self.niveau_administratif == 'region' and self.region:
            return self.region.nom
        elif self.niveau_administratif == 'departement' and self.departement:
            return self.departement.nom
        elif self.niveau_administratif == 'arrondissement' and self.arrondissement:
            return self.arrondissement.nom
        return "Zone inconnue"
    
    def get_zone_id(self):
        """Retourne l'ID de la zone administrative"""
        if self.niveau_administratif == 'region' and self.region:
            return self.region.id
        elif self.niveau_administratif == 'departement' and self.departement:
            return self.departement.id
        elif self.niveau_administratif == 'arrondissement' and self.arrondissement:
            return self.arrondissement.id
        return None