import random
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from geoprod_cm.models import Region, Departement, Arrondissement, Production


class Command(BaseCommand):
    help = 'Génère des données de production réalistes pour les tests'
    
    # Données réalistes par secteur
    PRODUITS = {
        'agriculture': {
            'Maïs': {'unite': 'tonnes', 'range': (5000, 50000)},
            'Manioc': {'unite': 'tonnes', 'range': (10000, 80000)},
            'Riz': {'unite': 'tonnes', 'range': (3000, 30000)},
            'Cacao': {'unite': 'tonnes', 'range': (2000, 25000)},
            'Café': {'unite': 'tonnes', 'range': (1000, 15000)},
            'Banane plantain': {'unite': 'tonnes', 'range': (8000, 60000)},
            'Arachide': {'unite': 'tonnes', 'range': (2000, 20000)},
            'Coton': {'unite': 'tonnes', 'range': (1000, 18000)},
            'Sorgho': {'unite': 'tonnes', 'range': (3000, 25000)},
            'Mil': {'unite': 'tonnes', 'range': (2000, 20000)},
        },
        'elevage': {
            'Bovins': {'unite': 'têtes', 'range': (10000, 200000)},
            'Ovins': {'unite': 'têtes', 'range': (5000, 100000)},
            'Caprins': {'unite': 'têtes', 'range': (8000, 150000)},
            'Porcins': {'unite': 'têtes', 'range': (3000, 50000)},
            'Volailles': {'unite': 'têtes', 'range': (50000, 500000)},
            'Lait': {'unite': 'litres', 'range': (100000, 2000000)},
            'Œufs': {'unite': 'milliers', 'range': (50000, 800000)},
        },
        'peche': {
            'Poisson frais': {'unite': 'tonnes', 'range': (1000, 15000)},
            'Poisson fumé': {'unite': 'tonnes', 'range': (500, 8000)},
            'Crevettes': {'unite': 'tonnes', 'range': (200, 5000)},
            'Tilapia': {'unite': 'tonnes', 'range': (800, 10000)},
            'Silure': {'unite': 'tonnes', 'range': (500, 7000)},
        }
    }
    
    # Spécialisation régionale (certaines régions produisent plus de certains produits)
    SPECIALISATIONS = {
        'Adamaoua': ['Bovins', 'Lait', 'Maïs', 'Sorgho'],
        'Centre': ['Manioc', 'Banane plantain', 'Cacao'],
        'Est': ['Manioc', 'Banane plantain', 'Poisson frais'],
        'Extrême-Nord': ['Coton', 'Mil', 'Sorgho', 'Bovins', 'Ovins'],
        'Littoral': ['Poisson frais', 'Crevettes', 'Banane plantain'],
        'Nord': ['Coton', 'Arachide', 'Bovins', 'Mil'],
        'Nord-Ouest': ['Café', 'Maïs', 'Volailles'],
        'Ouest': ['Café', 'Maïs', 'Volailles', 'Banane plantain'],
        'Sud': ['Cacao', 'Manioc', 'Poisson fumé'],
        'Sud-Ouest': ['Cacao', 'Banane plantain', 'Poisson frais'],
    }
    
    ANNEES = [2020, 2021, 2022, 2023, 2024]
    
    SOURCES = [
        'MINADER - Ministère de l\'Agriculture et du Développement Rural',
        'MINEPIA - Ministère de l\'Élevage, des Pêches et des Industries Animales',
        'INS - Institut National de la Statistique',
        'FAO - Organisation des Nations Unies pour l\'Alimentation et l\'Agriculture',
        'Enquête agricole annuelle',
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données de production existantes'
        )
        parser.add_argument(
            '--niveau',
            type=str,
            choices=['region', 'departement', 'arrondissement', 'tous'],
            default='tous',
            help='Niveau administratif pour lequel générer les données'
        )
        parser.add_argument(
            '--annees',
            type=int,
            default=3,
            help='Nombre d\'années de données à générer (max 5)'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Suppression des données de production...'))
            Production.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Données supprimées'))
        
        niveau = options['niveau']
        nb_annees = min(options['annees'], 5)
        annees = self.ANNEES[-nb_annees:]
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📊 GÉNÉRATION DES DONNÉES DE PRODUCTION'))
        self.stdout.write('='*60)
        self.stdout.write(f'Années: {", ".join(map(str, annees))}')
        self.stdout.write(f'Niveau: {niveau}')
        
        total_created = 0
        
        # Générer pour les régions
        if niveau in ['region', 'tous']:
            self.stdout.write('\n' + '-'*60)
            self.stdout.write('📍 Génération pour les RÉGIONS')
            self.stdout.write('-'*60)
            count = self.generate_for_regions(annees)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'✅ {count} enregistrements créés'))
        
        # Générer pour les départements
        if niveau in ['departement', 'tous']:
            self.stdout.write('\n' + '-'*60)
            self.stdout.write('📍 Génération pour les DÉPARTEMENTS')
            self.stdout.write('-'*60)
            count = self.generate_for_departements(annees)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'✅ {count} enregistrements créés'))
        
        # Générer pour les arrondissements (échantillon)
        if niveau in ['arrondissement', 'tous']:
            self.stdout.write('\n' + '-'*60)
            self.stdout.write('📍 Génération pour les ARRONDISSEMENTS (échantillon)')
            self.stdout.write('-'*60)
            count = self.generate_for_arrondissements(annees)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'✅ {count} enregistrements créés'))
        
        # Statistiques finales
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ GÉNÉRATION TERMINÉE'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total enregistrements créés: {total_created}')
        self.stdout.write(f'Total en base: {Production.objects.count()}')
        
        # Statistiques par secteur
        self.stdout.write('\nRépartition par secteur:')
        for secteur in ['agriculture', 'elevage', 'peche']:
            count = Production.objects.filter(secteur=secteur).count()
            self.stdout.write(f'  - {secteur.capitalize()}: {count}')
    
    def generate_for_regions(self, annees):
        """Génère des données pour toutes les régions"""
        regions = Region.objects.all()
        count = 0
        
        for region in regions:
            for annee in annees:
                for secteur, produits in self.PRODUITS.items():
                    for produit, config in produits.items():
                        # Vérifier si la région est spécialisée dans ce produit
                        is_specialized = produit in self.SPECIALISATIONS.get(region.nom, [])
                        
                        # Probabilité de production (plus élevée si spécialisé)
                        prob = 0.9 if is_specialized else 0.5
                        
                        if random.random() < prob:
                            quantite = self.generate_quantity(
                                config['range'], 
                                is_specialized,
                                annee
                            )
                            
                            Production.objects.create(
                                secteur=secteur,
                                produit=produit,
                                annee=annee,
                                niveau_administratif='region',
                                region=region,
                                quantite=quantite,
                                unite=config['unite'],
                                source_donnee=random.choice(self.SOURCES),
                                date_collecte=date(annee, 12, 31),
                            )
                            count += 1
        
        return count
    
    def generate_for_departements(self, annees):
        """Génère des données pour un échantillon de départements"""
        departements = Departement.objects.all()
        count = 0
        
        # Générer pour tous les départements mais avec moins de produits
        for dept in departements:
            region = dept.region
            
            for annee in annees:
                for secteur, produits in self.PRODUITS.items():
                    # Sélectionner un sous-ensemble de produits
                    produits_specialises = [
                        p for p in produits.keys() 
                        if p in self.SPECIALISATIONS.get(region.nom, [])
                    ]
                    
                    # Ajouter quelques produits aléatoires
                    autres_produits = random.sample(
                        [p for p in produits.keys() if p not in produits_specialises],
                        k=min(2, len(produits) - len(produits_specialises))
                    )
                    
                    produits_a_generer = produits_specialises + autres_produits
                    
                    for produit in produits_a_generer:
                        config = produits[produit]
                        is_specialized = produit in produits_specialises
                        
                        # Quantité réduite pour les départements (fraction de la région)
                        quantite = self.generate_quantity(
                            config['range'],
                            is_specialized,
                            annee,
                            factor=0.3  # 30% de la production régionale en moyenne
                        )
                        
                        Production.objects.create(
                            secteur=secteur,
                            produit=produit,
                            annee=annee,
                            niveau_administratif='departement',
                            departement=dept,
                            quantite=quantite,
                            unite=config['unite'],
                            source_donnee=random.choice(self.SOURCES),
                            date_collecte=date(annee, 12, 31),
                        )
                        count += 1
        
        return count
    
    def generate_for_arrondissements(self, annees):
        """Génère des données pour un échantillon d'arrondissements"""
        # Sélectionner 20% des arrondissements aléatoirement
        all_arrondissements = list(Arrondissement.objects.all())
        sample_size = max(20, len(all_arrondissements) // 5)
        arrondissements = random.sample(all_arrondissements, min(sample_size, len(all_arrondissements)))
        
        count = 0
        
        for arr in arrondissements:
            region = arr.departement.region
            
            for annee in annees:
                # Seulement quelques produits par arrondissement
                for secteur, produits in self.PRODUITS.items():
                    produits_specialises = [
                        p for p in produits.keys() 
                        if p in self.SPECIALISATIONS.get(region.nom, [])
                    ]
                    
                    # 1-2 produits spécialisés
                    produits_a_generer = random.sample(
                        produits_specialises if produits_specialises else list(produits.keys()),
                        k=min(2, len(produits))
                    )
                    
                    for produit in produits_a_generer:
                        config = produits[produit]
                        is_specialized = produit in produits_specialises
                        
                        # Quantité encore plus réduite pour les arrondissements
                        quantite = self.generate_quantity(
                            config['range'],
                            is_specialized,
                            annee,
                            factor=0.1  # 10% de la production régionale
                        )
                        
                        Production.objects.create(
                            secteur=secteur,
                            produit=produit,
                            annee=annee,
                            niveau_administratif='arrondissement',
                            arrondissement=arr,
                            quantite=quantite,
                            unite=config['unite'],
                            source_donnee=random.choice(self.SOURCES),
                            date_collecte=date(annee, 12, 31),
                        )
                        count += 1
        
        return count
    
    def generate_quantity(self, range_tuple, is_specialized, annee, factor=1.0):
        """Génère une quantité réaliste avec variation annuelle"""
        min_val, max_val = range_tuple
        
        # Ajuster selon la spécialisation
        if is_specialized:
            # Production plus élevée si spécialisé
            base = random.uniform(max_val * 0.6, max_val)
        else:
            # Production moyenne sinon
            base = random.uniform(min_val, max_val * 0.5)
        
        # Appliquer le facteur (pour départements/arrondissements)
        base *= factor
        
        # Variation annuelle légère (±10%)
        year_variation = 1 + random.uniform(-0.1, 0.1)
        
        # Tendance légère à la hausse au fil des années
        year_trend = 1 + (annee - 2020) * 0.02
        
        final_value = base * year_variation * year_trend
        
        return Decimal(str(round(final_value, 2)))
