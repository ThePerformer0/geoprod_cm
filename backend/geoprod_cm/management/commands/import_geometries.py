import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from geoprod_cm.models import Region, Departement, Arrondissement


class Command(BaseCommand):
    help = 'Importe les données géographiques complètes du Cameroun (régions, départements, arrondissements)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant l\'import'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Suppression des données existantes...'))
            Arrondissement.objects.all().delete()
            Departement.objects.all().delete()
            Region.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Données supprimées'))
        
        # Chemins vers les fichiers GeoJSON
        base_dir = settings.BASE_DIR
        data_dir = os.path.join(base_dir, 'data')
        
        regions_file = os.path.join(data_dir, 'gadm41_CMR_1.json')
        departements_file = os.path.join(data_dir, 'gadm41_CMR_2.json')
        arrondissements_file = os.path.join(data_dir, 'gadm41_CMR_3.json')
        
        # Import des régions
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📍 IMPORT DES RÉGIONS'))
        self.stdout.write('='*60)
        self.import_regions(regions_file)
        
        # Import des départements
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📍 IMPORT DES DÉPARTEMENTS'))
        self.stdout.write('='*60)
        self.import_departements(departements_file)
        
        # Import des arrondissements
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📍 IMPORT DES ARRONDISSEMENTS'))
        self.stdout.write('='*60)
        self.import_arrondissements(arrondissements_file)
        
        # Statistiques finales
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ IMPORT TERMINÉ'))
        self.stdout.write('='*60)
        self.stdout.write(f'Régions: {Region.objects.count()}')
        self.stdout.write(f'Départements: {Departement.objects.count()}')
        self.stdout.write(f'Arrondissements: {Arrondissement.objects.count()}')
    
    def import_regions(self, file_path):
        """Importe les régions depuis le fichier GeoJSON niveau 1"""
        
        # Informations complémentaires sur les régions
        regions_info = {
            "Adamaoua": {"code": "AD", "superficie": 63691},
            "Centre": {"code": "CE", "superficie": 68953},
            "Est": {"code": "ES", "superficie": 109011},
            "Extrême-Nord": {"code": "EN", "superficie": 34246},
            "Littoral": {"code": "LT", "superficie": 20239},
            "Nord": {"code": "NO", "superficie": 66090},
            "Nord-Ouest": {"code": "NW", "superficie": 17810},
            "Ouest": {"code": "OU", "superficie": 13872},
            "Sud": {"code": "SU", "superficie": 47110},
            "Sud-Ouest": {"code": "SW", "superficie": 25410},
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            created_count = 0
            updated_count = 0
            
            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                region_name = properties.get('NAME_1')
                
                if not region_name:
                    continue
                
                # Informations supplémentaires
                info = regions_info.get(region_name, {})
                
                # Calculer le centre
                center = self.calculate_center(geometry)
                
                # Créer ou mettre à jour
                region, created = Region.objects.update_or_create(
                    nom=region_name,
                    defaults={
                        'code': info.get('code', ''),
                        'geom_json': json.dumps(geometry),
                        'latitude': center[0] if center else None,
                        'longitude': center[1] if center else None,
                        'superficie': info.get('superficie'),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Créée: {region.nom}')
                else:
                    updated_count += 1
                    self.stdout.write(f'  📝 Mise à jour: {region.nom}')
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Régions: {created_count} créées, {updated_count} mises à jour'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {e}'))
    
    def import_departements(self, file_path):
        """Importe les départements depuis le fichier GeoJSON niveau 2"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                region_name = properties.get('NAME_1')
                dept_name = properties.get('NAME_2')
                
                if not region_name or not dept_name:
                    skipped_count += 1
                    continue
                
                # Trouver la région parente
                try:
                    region = Region.objects.get(nom=region_name)
                except Region.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠️  Région non trouvée: {region_name} pour {dept_name}'
                    ))
                    skipped_count += 1
                    continue
                
                # Calculer le centre
                center = self.calculate_center(geometry)
                
                # Créer ou mettre à jour
                dept, created = Departement.objects.update_or_create(
                    nom=dept_name,
                    region=region,
                    defaults={
                        'code': properties.get('HASC_2', '').split('.')[-1] if properties.get('HASC_2') else '',
                        'geom_json': json.dumps(geometry),
                        'latitude': center[0] if center else None,
                        'longitude': center[1] if center else None,
                    }
                )
                
                if created:
                    created_count += 1
                    if created_count % 10 == 0:
                        self.stdout.write(f'  ... {created_count} départements créés')
                else:
                    updated_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Départements: {created_count} créés, {updated_count} mis à jour, {skipped_count} ignorés'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {e}'))
    
    def import_arrondissements(self, file_path):
        """Importe les arrondissements depuis le fichier GeoJSON niveau 3"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                region_name = properties.get('NAME_1')
                dept_name = properties.get('NAME_2')
                arr_name = properties.get('NAME_3')
                
                if not region_name or not dept_name or not arr_name:
                    skipped_count += 1
                    continue
                
                # Trouver le département parent
                try:
                    departement = Departement.objects.get(nom=dept_name, region__nom=region_name)
                except Departement.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠️  Département non trouvé: {dept_name} ({region_name}) pour {arr_name}'
                    ))
                    skipped_count += 1
                    continue
                except Departement.MultipleObjectsReturned:
                    # Prendre le premier si plusieurs
                    departement = Departement.objects.filter(nom=dept_name, region__nom=region_name).first()
                
                # Calculer le centre
                center = self.calculate_center(geometry)
                
                # Créer ou mettre à jour
                arr, created = Arrondissement.objects.update_or_create(
                    nom=arr_name,
                    departement=departement,
                    defaults={
                        'code': properties.get('HASC_3', '').split('.')[-1] if properties.get('HASC_3') else '',
                        'geom_json': json.dumps(geometry),
                        'latitude': center[0] if center else None,
                        'longitude': center[1] if center else None,
                    }
                )
                
                if created:
                    created_count += 1
                    if created_count % 50 == 0:
                        self.stdout.write(f'  ... {created_count} arrondissements créés')
                else:
                    updated_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Arrondissements: {created_count} créés, {updated_count} mis à jour, {skipped_count} ignorés'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {e}'))
    
    def calculate_center(self, geometry):
        """Calcule le centre approximatif d'une géométrie"""
        try:
            coords = None
            
            if geometry['type'] == 'Polygon':
                coords = geometry['coordinates'][0][0]
            elif geometry['type'] == 'MultiPolygon':
                coords = geometry['coordinates'][0][0][0]
            
            if coords:
                return [coords[1], coords[0]]  # [lat, lng]
        except:
            pass
        
        return None
