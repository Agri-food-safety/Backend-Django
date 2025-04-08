import json
from django.core.management.base import BaseCommand
from core.models import PestType

class Command(BaseCommand):
    help = 'Seeds pest data from pests.json file'

    def handle(self, *args, **kwargs):
        try:
            # Read the JSON file
            with open('agriscan/data/pests.json', 'r', encoding='utf-8') as file:
                pests_data = json.load(file)

            # Create pest types
            for pest in pests_data:
                PestType.objects.create(
                    name=pest['name'],
                    description=pest['description'],
                    treatment=pest['treatment'],
                    severity=pest['severity']
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(pests_data)} pest types'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding pest data: {str(e)}')) 