from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Report, PlantType, DiseaseType, PestType, User
import csv
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seeds reports data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--supabase-url', type=str, default='https://gktbuzdsfdyukggnipqd.supabase.co/storage/v1/object/public/plants/',
                          help='Supabase storage URL')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        supabase_url = options['supabase_url']

        # Get the default user
        default_user = User.objects.get(id='fee1530c-e457-453e-971d-cb637f842b7a')

        # Get all plant types, disease types, and pest types
        plant_types = {pt.name.lower(): pt for pt in PlantType.objects.all()}
        disease_types = {dt.name.lower(): dt for dt in DiseaseType.objects.all()}
        pest_types = {pt.name.lower(): pt for pt in PestType.objects.all()}

        # Generate random locations in Algeria
        def random_location():
            # Rough bounding box for Algeria
            lat = random.uniform(18.0, 37.0)   # from Sahara to Mediterranean
            lng = random.uniform(-8.7, 11.9)   # from western to eastern border
            return lat, lng

        # Generate random cities and states
        cities = [
        'Algiers', 'Oran', 'Constantine', 'Annaba', 'Blida',
        'Batna', 'Sétif', 'Tlemcen', 'Tizi Ouzou', 'Béjaïa'
    ]

        states = [
            'Algiers', 'Oran', 'Constantine', 'Annaba', 'Blida',
            'Batna', 'Sétif', 'Tlemcen', 'Tizi Ouzou', 'Béjaïa'
        ]

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            reports_to_create = []

            for row in reader:
                # Get the plant type
                plant_name = row['plant_name'].lower()
                if plant_name not in plant_types:
                    self.stdout.write(self.style.WARNING(f"Plant type not found: {plant_name}"))
                    continue

                # Generate random confidence values
                plant_confidence = random.uniform(0.85, 0.99)
                disease_confidence = random.uniform(0.85, 0.99) if row['disease'] != 'healthy' else 0.0
                pest_confidence = random.uniform(0.85, 0.99) if row['pest_risk'] != 'low' else 0.0

                # Get disease type if not healthy
                disease_type = None
                if row['disease'] != 'healthy':
                    disease_name = row['disease'].lower()
                    if disease_name in disease_types:
                        disease_type = disease_types[disease_name]

                # Get pest type based on risk level
                pest_type = None
                if row['pest_risk'] != 'low':
                    # Randomly select a pest type
                    pest_type = random.choice(list(pest_types.values()))

                # Generate random timestamp within the last 30 days
                timestamp = timezone.now() - timedelta(days=random.randint(0, 30))

                # Generate random location
                lat, lng = random_location()
                city = random.choice(cities)
                state = random.choice(states)

                # Create the report
                report = Report(
                    user=default_user,
                    plant_type=plant_types[plant_name],
                    image_url=f"{supabase_url}{row['image_path']}",
                    timestamp=timestamp,
                    gps_lat=lat,
                    gps_lng=lng,
                    city=city,
                    state=state,
                    plant_detection={
                        'confidence': plant_confidence,
                        'plant_type_id': str(plant_types[plant_name].id)
                    },
                    disease_detection={
                        'confidence': disease_confidence,
                        'disease_type_id': str(disease_type.id) if disease_type else None
                    } if disease_type else None,
                    pest_detection={
                        'confidence': pest_confidence,
                        'pest_type_id': str(pest_type.id) if pest_type else None
                    } if pest_type else None,
                    drought_detection={
                        'level': row['drought_stress_level'] if row['drought_stress_level'] else None
                    } if row['drought_stress_level'] else None
                )
                reports_to_create.append(report)

            # Bulk create the reports
            Report.objects.bulk_create(reports_to_create)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(reports_to_create)} reports'))