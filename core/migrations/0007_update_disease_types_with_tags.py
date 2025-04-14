from django.db import migrations

def update_disease_types(apps, schema_editor):
    DiseaseType = apps.get_model('core', 'DiseaseType')
    PlantType = apps.get_model('core', 'PlantType')
    
    # Get plant type IDs from database for mapping
    plant_ids = {
        'apple': '44220193-fc8d-40ae-a898-724fc3aa6a8d',
        'bean': 'd7007ae1-600d-433f-8d6f-743966932888',
        'blueberry': '47a854b0-ee6c-4fee-bc07-8f92cda04b9a', 
        'cherry': 'e5b39a70-d5b4-4620-9cbc-c39c8711ff7f',
        'corn': 'ad5bdf18-0dbf-476d-bfd4-a31a7e2f5e79',
        'date_palm': 'd7881107-6d43-42d6-a297-e4c90b0c15f4',
        'grape': 'cd704a7a-0779-4601-9d3f-7bf068ee94e9',
        'olive': 'de582271-eed5-45f0-b518-20c169bd5954',
        'orange': 'b3a6209f-55ac-4a84-913b-b9117037b571',
        'peach': 'b9a8f1af-eb85-4fbc-b024-ef686810230c',
        'pepper': 'bd0ab3a6-0690-4b45-9747-44cdcd2eb071',
        'potato': 'fb5fef6b-4f4e-4f9c-87c0-fc9ebf70cbee',
        'raspberry': 'f1d9ec9a-bde2-4b6f-a42d-b224ce2763d7',
        'rice': 'f2da7b80-40b7-4196-bfd5-f9e82d28158d',
        'soybean': 'ac9c6d61-fc5d-4c32-8bff-05ce589bad8e',
        'squash': '049dae7e-4385-42f7-9488-586914960d64',
        'strawberry': 'd1c7f7c1-5893-4c80-8f2b-ebea01b336e1',
        'tomato': '499a0376-4f96-40ca-a20c-e0851d55afd6',
        'wheat': '06674266-b168-43c1-83a2-532695d7f461',
    }
    
    # Define the disease types with proper tags and Arabic content
    disease_data = [
        # Apple Diseases
        {
            'name': 'Apple Scab',
            'tag': 'apple_apple_scab',
            'description': 'مرض فطري يسبب بقع داكنة وجرب على الأوراق والفواكه.',
            'treatment': 'رش المبيدات الفطرية في أوائل الربيع، وإزالة الأوراق المتساقطة، والتقليم لتحسين دوران الهواء.',
            'plant_types': [plant_ids['apple']],
            'severity': 'medium'
        },
        {
            'name': 'Apple Black Rot',
            'tag': 'apple_black_rot',
            'description': 'مرض فطري يسبب بقع الأوراق وتعفن الفاكهة والتقرحات على الفروع.',
            'treatment': 'تقليم الفروع المصابة، وإزالة الفواكه المتحجرة، ورش المبيدات الفطرية.',
            'plant_types': [plant_ids['apple']],
            'severity': 'high'
        },
        {
            'name': 'Cedar Apple Rust',
            'tag': 'apple_cedar_apple_rust',
            'description': 'مرض فطري يسبب بقع برتقالية على الأوراق وأحيانًا على الفواكه.',
            'treatment': 'إزالة أشجار الأرز القريبة إن أمكن، ورش المبيدات الفطرية، واختيار الأصناف المقاومة.',
            'plant_types': [plant_ids['apple']],
            'severity': 'medium'
        },
        
        # Bean Diseases
        {
            'name': 'Bean Angular Leaf Spot',
            'tag': 'bean_angular_leaf_spot',
            'description': 'مرض بكتيري يسبب آفات زاوية مشبعة بالماء على الأوراق.',
            'treatment': 'استخدام المبيدات البكتيرية النحاسية، وممارسة تناوب المحاصيل، وتجنب الري العلوي.',
            'plant_types': [plant_ids['bean']],
            'severity': 'medium'
        },
        {
            'name': 'Bean Rust',
            'tag': 'bean_bean_rust',
            'description': 'مرض فطري يسبب بثور صدئية على الجانب السفلي من الأوراق.',
            'treatment': 'رش المبيدات الفطرية، وزيادة المسافة بين النباتات، واختيار الأصناف المقاومة.',
            'plant_types': [plant_ids['bean']],
            'severity': 'medium'
        },
        
        # Corn Diseases
        {
            'name': 'Gray Leaf Spot',
            'tag': 'corn_(maize)_cercospora_leaf_spot_gray_leaf_spot',
            'description': 'مرض فطري يسبب آفات رمادية إلى بنية مستطيلة على أوراق الذرة.',
            'treatment': 'تناوب المحاصيل، واستخدام الهجن المقاومة، ورش المبيدات الفطرية عند الحاجة.',
            'plant_types': [plant_ids['corn']],
            'severity': 'medium'
        },
        {
            'name': 'Common Rust',
            'tag': 'corn_(maize)_common_rust_',
            'description': 'مرض فطري ينتج بثور صدئية اللون على سطحي الورقة.',
            'treatment': 'زراعة الأصناف المقاومة، ورش المبيدات الفطرية، والحفاظ على نظافة الحقل.',
            'plant_types': [plant_ids['corn']],
            'severity': 'medium'
        },
        {
            'name': 'Northern Leaf Blight',
            'tag': 'corn_(maize)_northern_leaf_blight',
            'description': 'مرض فطري يسبب آفات كبيرة على شكل سيجار رمادية خضراء إلى سمراء.',
            'treatment': 'استخدام الهجن المقاومة، وتناوب المحاصيل، ورش المبيدات الفطرية.',
            'plant_types': [plant_ids['corn']],
            'severity': 'high'
        },
        
        # Date Palm Diseases
        {
            'name': 'Brown Spots',
            'tag': 'date_palm_brown_spots',
            'description': 'مرض فطري يسبب بقع بنية على السعف والثمار.',
            'treatment': 'تقليم السعف المصاب، ورش المبيدات الفطرية، والحفاظ على صحة الشجرة.',
            'plant_types': [plant_ids['date_palm']],
            'severity': 'medium'
        },
        {
            'name': 'White Scale',
            'tag': 'date_palm_white_scale',
            'description': 'إصابة بالحشرات القشرية التي تسبب ترسبات شمعية بيضاء على السعف.',
            'treatment': 'رش الزيوت البستانية، وتشجيع الحشرات المفيدة، وتقليم الأجزاء المصابة بشدة.',
            'plant_types': [plant_ids['date_palm']],
            'severity': 'high'
        },
        
        # Grape Diseases
        {
            'name': 'Black Rot',
            'tag': 'grape_black_rot',
            'description': 'مرض فطري يسبب آفات سوداء دائرية على الأوراق وتعفن الفاكهة.',
            'treatment': 'التقليم لزيادة تدفق الهواء، ورش المبيدات الفطرية، وإزالة البقايا المصابة.',
            'plant_types': [plant_ids['grape']],
            'severity': 'high'
        },
        {
            'name': 'Esca (Black Measles)',
            'tag': 'grape_esca_(black_measles)',
            'description': 'مرض فطري معقد يسبب أنماط ورقية مخططة كالنمر وفاكهة مبقعة.',
            'treatment': 'إزالة الكروم المصابة، واستخدام واقيات الجروح، والحفاظ على صحة الكرمة.',
            'plant_types': [plant_ids['grape']],
            'severity': 'high'
        },
        {
            'name': 'Leaf Blight (Isariopsis Leaf Spot)',
            'tag': 'grape_leaf_blight_(isariopsis_leaf_spot)',
            'description': 'مرض فطري يسبب بقع حمراء بنية مع هالات صفراء على الأوراق.',
            'treatment': 'رش المبيدات الفطرية، وتحسين دوران الهواء، وممارسة النظافة السليمة.',
            'plant_types': [plant_ids['grape']],
            'severity': 'medium'
        },
        
        # Continue with other diseases...
        # Tomato Diseases
        {
            'name': 'Tomato Early Blight',
            'tag': 'tomato_early_blight',
            'description': 'مرض فطري يسبب بقع على شكل هدف على الأوراق السفلية أولاً.',
            'treatment': 'رش المبيدات الفطرية، وممارسة تناوب المحاصيل، وضمان تغذية النبات الكافية.',
            'plant_types': [plant_ids['tomato']],
            'severity': 'medium'
        },
        {
            'name': 'Tomato Late Blight',
            'tag': 'tomato_late_blight',
            'description': 'مرض مدمر يمكن أن يدمر محاصيل الطماطم بأكملها.',
            'treatment': 'رش المبيدات الفطرية وقائياً، وإزالة النباتات المصابة، وضمان دوران الهواء الجيد.',
            'plant_types': [plant_ids['tomato']],
            'severity': 'high'
        },
        
        # Potato Diseases
        {
            'name': 'Potato Early Blight',
            'tag': 'potato_early_blight',
            'description': 'مرض فطري يسبب بقع داكنة على شكل هدف على الأوراق السفلية أولاً.',
            'treatment': 'رش المبيدات الفطرية، وممارسة تناوب المحاصيل، وضمان تغذية النبات الكافية.',
            'plant_types': [plant_ids['potato']],
            'severity': 'medium'
        },
        {
            'name': 'Potato Late Blight',
            'tag': 'potato_late_blight',
            'description': 'مرض فطري مدمر ينتشر بسرعة ويمكن أن يقضي على محصول البطاطس بالكامل.',
            'treatment': 'رش المبيدات الفطرية وقائياً، وإزالة النباتات المصابة، وتجنب ظروف الرطوبة العالية.',
            'plant_types': [plant_ids['potato']],
            'severity': 'high'
        },
        
        # Wheat Diseases
        {
            'name': 'Wheat Aphid',
            'tag': 'wheat_aphid',
            'description': 'آفة حشرية تمتص العصارة من أوراق القمح وسيقانه، مما يؤدي إلى تلف النبات.',
            'treatment': 'رش المبيدات الحشرية، وتشجيع الحشرات المفترسة الطبيعية، واستخدام الأصناف المقاومة.',
            'plant_types': [plant_ids['wheat']],
            'severity': 'medium'
        },
        {
            'name': 'Wheat Black Rust',
            'tag': 'wheat_black_rust',
            'description': 'مرض فطري يسبب بثور سوداء على ساق القمح وأوراقه.',
            'treatment': 'استخدام الأصناف المقاومة، ورش المبيدات الفطرية، وإزالة العوائل البديلة.',
            'plant_types': [plant_ids['wheat']],
            'severity': 'high'
        },
        {
            'name': 'Wheat Yellow Rust',
            'tag': 'wheat_yellow_rust',
            'description': 'مرض فطري يسبب شرائط صفراء من البثور على أوراق القمح.',
            'treatment': 'زراعة أصناف مقاومة، والرش المبكر بالمبيدات الفطرية، ومراقبة الحقول باستمرار.',
            'plant_types': [plant_ids['wheat']],
            'severity': 'high'
        }
    ]
    
    # Update or create disease types with new information
    for data in disease_data:
        DiseaseType.objects.update_or_create(
            name=data['name'],
            defaults={
                'tag': data['tag'],
                'description': data['description'],
                'treatment': data['treatment'],
                'plant_types': data['plant_types'],
                'severity': data['severity']
            }
        )

def reverse_update(apps, schema_editor):
    # This is a data migration that adds or updates data, so the reverse operation is a no-op
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_diseasetype_tag'),
    ]

    operations = [
        migrations.RunPython(
            update_disease_types,
            reverse_update
        ),
    ]