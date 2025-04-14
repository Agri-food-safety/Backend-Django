from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_update_disease_types_with_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='diseasetype',
            name='arabic_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]