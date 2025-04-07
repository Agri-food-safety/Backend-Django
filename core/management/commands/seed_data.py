from django.core.management.base import BaseCommand
from core.models import PlantType, DiseaseType, User, Report, Alert, PestType
from django.utils import timezone
from datetime import timedelta
import random
import uuid
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds the database with plant, disease, user, report, and alert data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-delete',
            action='store_true',
            help='Do not delete existing data before seeding',
        )

    def handle(self, *args, **options):
        fake = Faker(['en_US'])

        # Delete existing data first unless --no-delete is specified
        if not options['no_delete']:
            self.stdout.write(self.style.WARNING('Deleting all existing data...'))
            Alert.objects.all().delete()
            Report.objects.all().delete()
            PestType.objects.all().delete()
            DiseaseType.objects.all().delete()
            PlantType.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()  # Keep superusers
            self.stdout.write(self.style.SUCCESS('All existing data deleted'))

        # Algerian cities for more realistic location data
        algerian_cities = [
            "Algiers", "Oran", "Constantine", "Annaba", "Blida",
            "Batna", "Sétif", "Chlef", "Djelfa", "Biskra",
            "Tébessa", "Tiaret", "Tlemcen", "Bejaia", "Ouargla",
            "Sidi Bel Abbès", "Béchar", "Skikda", "Mostaganem", "Msila"
        ]
        
        plants_data = [
            {"name": "Apple", "scientificName": "Malus domestica"},
            {"name": "Bean", "scientificName": "Phaseolus vulgaris"},
            {"name": "Blueberry", "scientificName": "Vaccinium corymbosum"},
            {"name": "Cherry (including sour)", "scientificName": "Prunus avium"},
            {"name": "Corn (Maize)", "scientificName": "Zea mays"},
            {"name": "Date Palm", "scientificName": "Phoenix dactylifera"},
            {"name": "Grape", "scientificName": "Vitis vinifera"},
            {"name": "Olive", "scientificName": "Olea europaea"},
            {"name": "Orange", "scientificName": "Citrus sinensis"},
            {"name": "Peach", "scientificName": "Prunus persica"},
            {"name": "Pepper, Bell", "scientificName": "Capsicum annuum"},
            {"name": "Potato", "scientificName": "Solanum tuberosum"},
            {"name": "Raspberry", "scientificName": "Rubus idaeus"},
            {"name": "Rice", "scientificName": "Oryza sativa"},
            {"name": "Soybean", "scientificName": "Glycine max"},
            {"name": "Squash", "scientificName": "Cucurbita pepo"},
            {"name": "Strawberry", "scientificName": "Fragaria × ananassa"},
            {"name": "Tomato", "scientificName": "Solanum lycopersicum"},
            {"name": "Wheat", "scientificName": "Triticum aestivum"}
        ]

        diseases_data = [
            {"name": "Apple Scab", "scientificName": "Venturia inaequalis", "affectedPlants": ["Apple"], "severity": "high"},
            {"name": "Black Rot", "scientificName": "Diplodia seriata", "affectedPlants": ["Apple", "Grape"], "severity": "high"},
            {"name": "Cedar Apple Rust", "scientificName": "Gymnosporangium juniper-virginianae", "affectedPlants": ["Apple"], "severity": "medium"},
            {"name": "Angular Leaf Spot", "scientificName": "Pseudomonas syringae pv. phaseolicola", "affectedPlants": ["Bean"], "severity": "medium"},
            {"name": "Bean Rust", "scientificName": "Uromyces appendiculatus", "affectedPlants": ["Bean"], "severity": "high"},
            {"name": "Powdery Mildew", "scientificName": "Erysiphe spp.", "affectedPlants": ["Cherry (including sour)", "Squash"], "severity": "medium"},
            {"name": "Cercospora Leaf Spot Gray Leaf Spot", "scientificName": "Cercospora zeae-maydis", "affectedPlants": ["Corn (Maize)"], "severity": "high"},
            {"name": "Common Rust", "scientificName": "Puccinia sorghi", "affectedPlants": ["Corn (Maize)"], "severity": "medium"},
            {"name": "Northern Leaf Blight", "scientificName": "Exserohilum turcicum", "affectedPlants": ["Corn (Maize)"], "severity": "high"},
            {"name": "Brown Spots", "scientificName": "Alternaria alternata", "affectedPlants": ["Date Palm"], "severity": "medium"},
            {"name": "White Scale", "scientificName": "Aonidiella aurantii", "affectedPlants": ["Date Palm"], "severity": "high"},
            {"name": "Esca (Black Measles)", "scientificName": "Phaeomoniella chlamydospora", "affectedPlants": ["Grape"], "severity": "high"},
            {"name": "Leaf Blight (Isariopsis Leaf Spot)", "scientificName": "Isariopsis griseola", "affectedPlants": ["Grape"], "severity": "medium"},
            {"name": "Haunglongbing (Citrus Greening)", "scientificName": "Candidatus Liberibacter asiaticus", "affectedPlants": ["Orange"], "severity": "high"},
            {"name": "Bacterial Spot", "scientificName": "Xanthomonas campestris pv. vesicatoria", "affectedPlants": ["Peach", "Pepper, Bell"], "severity": "high"},
            {"name": "Early Blight", "scientificName": "Alternaria solani", "affectedPlants": ["Potato", "Tomato"], "severity": "high"},
            {"name": "Late Blight", "scientificName": "Phytophthora infestans", "affectedPlants": ["Potato", "Tomato"], "severity": "high"},
            {"name": "Leaf Mold", "scientificName": "Fulvia fulva", "affectedPlants": ["Tomato"], "severity": "medium"},
            {"name": "Septoria Leaf Spot", "scientificName": "Septoria lycopersici", "affectedPlants": ["Tomato"], "severity": "high"},
            {"name": "Spider Mites (Two-Spotted Spider Mite)", "scientificName": "Tetranychus urticae", "affectedPlants": ["Tomato"], "severity": "medium"},
            {"name": "Target Spot", "scientificName": "Corynespora cassiicola", "affectedPlants": ["Tomato"], "severity": "medium"},
            {"name": "Tomato Mosaic Virus", "scientificName": "Tomato mosaic virus", "affectedPlants": ["Tomato"], "severity": "high"},
            {"name": "Tomato Yellow Leaf Curl Virus", "scientificName": "Tomato yellow leaf curl virus", "affectedPlants": ["Tomato"], "severity": "high"},
            {"name": "Aphid", "scientificName": "Aphidoidea", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Black Rust", "scientificName": "Puccinia graminis", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Blast", "scientificName": "Magnaporthe oryzae", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Brown Rust", "scientificName": "Puccinia triticina", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Common Root Rot", "scientificName": "Fusarium solani", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Fusarium Head Blight", "scientificName": "Fusarium graminearum", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Leaf Blight", "scientificName": "Cochliobolus sativus", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Mildew", "scientificName": "Erysiphe graminis", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Mite", "scientificName": "Acarus spp.", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Septoria", "scientificName": "Septoria tritici", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Smut", "scientificName": "Ustilago tritici", "affectedPlants": ["Wheat"], "severity": "high"},
            {"name": "Stem Fly", "scientificName": "Atherigona", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Tan Spot", "scientificName": "Pyrenophora tritici-repentis", "affectedPlants": ["Wheat"], "severity": "medium"},
            {"name": "Yellow Rust", "scientificName": "Puccinia striiformis", "affectedPlants": ["Wheat"], "severity": "high"}
        ]

        # Create pest types based on diseases with modifications for variety
        pests_data = [
            {"name": "Aphids", "description": "Small sap-sucking insects", "severity": "medium"},
            {"name": "Whiteflies", "description": "Small white flying insects that feed on plant sap", "severity": "medium"},
            {"name": "Spider Mites", "description": "Tiny arachnids that cause stippling on leaves", "severity": "high"},
            {"name": "Thrips", "description": "Slender insects with fringed wings", "severity": "medium"},
            {"name": "Caterpillars", "description": "Larvae of butterflies and moths", "severity": "high"},
            {"name": "Mealybugs", "description": "Unarmored scale insects with white waxy coating", "severity": "medium"},
            {"name": "Cutworms", "description": "Larvae that cut down plants at the soil line", "severity": "high"},
            {"name": "Nematodes", "description": "Microscopic worms that damage roots", "severity": "high"},
            {"name": "Grasshoppers", "description": "Large jumping insects that consume large amounts of foliage", "severity": "medium"},
            {"name": "Beetles", "description": "Hard-shelled insects that chew on plant material", "severity": "medium"},
        ]

        # Define geographic boundaries for Algeria (used for random GPS locations)
        min_lat = 19.0574
        max_lat = 37.1184
        min_lng = -8.6844
        max_lng = 11.9995

        # Create plant types
        plant_instances = []
        for plant in plants_data:
            # Add random common diseases for each plant
            common_diseases = random.sample([d["name"] for d in diseases_data], random.randint(2, 5))
            plant_instance = PlantType.objects.create(
                id=uuid.uuid4(),
                name=plant["name"],
                scientific_name=plant["scientificName"],
                common_diseases=common_diseases
            )
            plant_instances.append(plant_instance)
            self.stdout.write(self.style.SUCCESS(f'Created plant: {plant_instance.name}'))

        # Create disease types
        disease_instances = []
        for disease in diseases_data:
            # Find plant IDs based on names
            plant_type_ids = []
            for plant_name in disease["affectedPlants"]:
                matching_plants = [p for p in plant_instances if p.name == plant_name]
                plant_type_ids.extend([str(p.id) for p in matching_plants])
                
            # If no matches found, assign to random plants
            if not plant_type_ids:
                random_plants = random.sample(plant_instances, random.randint(1, 3))
                plant_type_ids = [str(p.id) for p in random_plants]
                
            disease_instance = DiseaseType.objects.create(
                id=uuid.uuid4(),
                name=disease["name"],
                description=fake.paragraph(),
                treatment=fake.paragraph(),
                plant_types=plant_type_ids,
                severity=disease["severity"]
            )
            disease_instances.append(disease_instance)
            self.stdout.write(self.style.SUCCESS(f'Created disease: {disease_instance.name}'))
        
        # Create pest types
        pest_instances = []
        for pest in pests_data:
            # Assign to random plants
            random_plants = random.sample(plant_instances, random.randint(2, 6))
            plant_type_ids = [str(p.id) for p in random_plants]
                
            pest_instance = PestType.objects.create(
                id=uuid.uuid4(),
                name=pest["name"],
                description=pest["description"] + ". " + fake.paragraph(),
                treatment=fake.paragraph(),
                plant_types=plant_type_ids,
                severity=pest["severity"]
            )
            pest_instances.append(pest_instance)
            self.stdout.write(self.style.SUCCESS(f'Created pest: {pest_instance.name}'))

        # Create dummy users
        num_users = 10
        users = []
        for _ in range(num_users):
            # Generate unique phone number
            phone = f"+213{random.randint(500000000, 799999999)}"
            
            city = random.choice(algerian_cities)
            user = User.objects.create_user(
                phone=phone,
                full_name=fake.name(),
                role=random.choice(['farmer', 'inspector']),
                city=city,
                state=random.choice(['Algiers', 'Oran', 'Constantine', 'Annaba', 'Batna']),
                gps_lat=random.uniform(min_lat, max_lat),
                gps_lng=random.uniform(min_lng, max_lng),
                password="password123" if _ == 0 else fake.password(length=random.randint(8, 14))
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.full_name} ({user.phone})'))
            # Mark the first user's password for easy login
            if _ == 0:
                self.stdout.write(self.style.WARNING(f'First user created with phone: {user.phone} and password: password123'))
            users.append(user)

        # Create dummy reports
        num_reports = 30
        for _ in range(num_reports):
            user = random.choice(users)
            plant_type = random.choice(plant_instances)
            disease = random.choice(disease_instances)
            pest = random.choice(pest_instances)
            
            # Generate location data - either user's location or random
            use_user_location = random.choice([True, False])
            
            if use_user_location:
                gps_lat = user.gps_lat
                gps_lng = user.gps_lng
                city = user.city
                state = user.state
            else:
                gps_lat = random.uniform(min_lat, max_lat)
                gps_lng = random.uniform(min_lng, max_lng)
                city = random.choice(algerian_cities)
                state = random.choice(['Algiers', 'Oran', 'Constantine', 'Annaba', 'Batna'])
            
            # Random detection results
            plant_detection = {'plantId': str(plant_type.id), 'confidence': round(random.uniform(0.7, 0.99), 2)}
            disease_detection = {'diseaseId': str(disease.id), 'confidence': round(random.uniform(0.65, 0.95), 2)}
            pest_detection = {'pestId': str(pest.id), 'confidence': round(random.uniform(0.6, 0.9), 2)}
            drought_detection = {'droughtLevel': random.randint(0, 5), 'confidence': round(random.uniform(0.7, 0.95), 2)}
            
            # Create report with randomized review status
            is_reviewed = random.choice([True, False])
            reviewer = random.choice(users) if is_reviewed else None
            reviewed_at = timezone.now() - timedelta(days=random.randint(1, 10)) if is_reviewed else None
            
            report = Report.objects.create(
                user=user,
                plant_type=plant_type,
                image_url=f"https://picsum.photos/id/{random.randint(1, 1000)}/800/600",
                gps_lat=gps_lat,
                gps_lng=gps_lng,
                city=city,
                state=state,
                plant_detection=plant_detection,
                disease_detection=disease_detection,
                pest_detection=pest_detection,
                drought_detection=drought_detection,
                status='reviewed' if is_reviewed else 'submitted',
                notes=fake.paragraph() if is_reviewed else '',
                reviewed_by=reviewer,
                reviewed_at=reviewed_at
            )
            self.stdout.write(self.style.SUCCESS(f'Created report: {report.id} ({report.status})'))

        # Create dummy alerts with varied expiry dates
        num_alerts = 8
        for _ in range(num_alerts):
            user = random.choice(users)
            # Randomize alert creation and expiry times
            days_ago = random.randint(0, 14)
            expires_in = random.randint(7, 60)
            created_at = timezone.now() - timedelta(days=days_ago)
            expires_at = created_at + timedelta(days=expires_in)
            
            alert = Alert.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(),
                severity=random.choice(['info', 'warning', 'danger']),
                target_state=random.choice(['Algiers', 'Oran', 'Constantine', 'Annaba', 'Batna']),
                target_city=random.choice([None, random.choice(algerian_cities)]),
                created_by=user,
                created_at=created_at,
                expires_at=expires_at
            )
            self.stdout.write(self.style.SUCCESS(f'Created alert: {alert.title}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded database with:'))
        self.stdout.write(self.style.SUCCESS(f'- {len(plant_instances)} plants'))
        self.stdout.write(self.style.SUCCESS(f'- {len(disease_instances)} diseases'))
        self.stdout.write(self.style.SUCCESS(f'- {len(pest_instances)} pests'))
        self.stdout.write(self.style.SUCCESS(f'- {len(users)} users'))
        self.stdout.write(self.style.SUCCESS(f'- {num_reports} reports'))
        self.stdout.write(self.style.SUCCESS(f'- {num_alerts} alerts'))