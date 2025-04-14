from django.db import migrations

def add_arabic_names(apps, schema_editor):
    DiseaseType = apps.get_model('core', 'DiseaseType')
    
    # Mapping of disease tags to their Arabic names
    arabic_names = {
        'apple_apple_scab': 'جرب التفاح',
        'apple_black_rot': 'العفن الأسود في التفاح',
        'apple_cedar_apple_rust': 'صدأ التفاح السروي',
        'apple_healthy': 'تفاح سليم',
        'bean_angular_leaf_spot': 'التبقع الزاوي لأوراق الفاصوليا',
        'bean_bean_rust': 'صدأ الفاصوليا',
        'bean_healthy': 'فاصوليا سليمة',
        'blueberry_healthy': 'توت أزرق سليم',
        'cherry_(including_sour)_healthy': 'كرز سليم',
        'cherry_(including_sour)_powdery_mildew': 'البياض الدقيقي للكرز',
        'corn_(maize)_cercospora_leaf_spot_gray_leaf_spot': 'التبقع الرمادي لأوراق الذرة',
        'corn_(maize)_common_rust_': 'الصدأ الشائع في الذرة',
        'corn_(maize)_healthy': 'ذرة سليمة',
        'corn_(maize)_northern_leaf_blight': 'لفحة أوراق الذرة الشمالية',
        'date_palm_brown_spots': 'البقع البنية في نخيل التمر',
        'date_palm_healthy': 'نخيل تمر سليم',
        'date_palm_white_scale': 'الحشرة القشرية البيضاء في نخيل التمر',
        'grape_black_rot': 'العفن الأسود في العنب',
        'grape_esca_(black_measles)': 'الإسكا (الحصبة السوداء) في العنب',
        'grape_healthy': 'عنب سليم',
        'grape_leaf_blight_(isariopsis_leaf_spot)': 'لفحة أوراق العنب (تبقع أيساريوبسيس)',
        'olive_kus_gozu_mantari': 'فطر عين الطير في الزيتون',
        'olive_pas_akari': 'عث الزيتون',
        'olive_saglikli': 'زيتون سليم',
        'orange_haunglongbing_(citrus_greening)': 'اخضرار الحمضيات',
        'peach_bacterial_spot': 'التبقع البكتيري في الخوخ',
        'peach_healthy': 'خوخ سليم',
        'pepper,_bell_bacterial_spot': 'التبقع البكتيري في الفلفل',
        'pepper,_bell_healthy': 'فلفل سليم',
        'potato_early_blight': 'اللفحة المبكرة في البطاطس',
        'potato_healthy': 'بطاطس سليمة',
        'potato_late_blight': 'اللفحة المتأخرة في البطاطس',
        'raspberry_healthy': 'توت العليق السليم',
        'rice_bacterial_leaf_blight': 'لفحة الأوراق البكتيرية في الأرز',
        'rice_brown_spot': 'البقعة البنية في الأرز',
        'rice_healthy_rice_leaf': 'أوراق أرز سليمة',
        'rice_leaf_blast': 'لفحة أوراق الأرز',
        'rice_leaf_scald': 'سفعة أوراق الأرز',
        'rice_sheath_blight': 'لفحة غمد الأرز',
        'soybean_healthy': 'فول الصويا السليم',
        'squash_powdery_mildew': 'البياض الدقيقي في القرع',
        'strawberry_healthy': 'فراولة سليمة',
        'strawberry_leaf_scorch': 'حرق أوراق الفراولة',
        'tomato_bacterial_spot': 'التبقع البكتيري في الطماطم',
        'tomato_early_blight': 'اللفحة المبكرة في الطماطم',
        'tomato_healthy': 'طماطم سليمة',
        'tomato_late_blight': 'اللفحة المتأخرة في الطماطم',
        'tomato_leaf_mold': 'عفن أوراق الطماطم',
        'tomato_septoria_leaf_spot': 'تبقع سبتوريا في أوراق الطماطم',
        'tomato_spider_mites_two-spotted_spider_mite': 'عناكب الطماطم ذات البقعتين',
        'tomato_target_spot': 'البقعة المستهدفة في الطماطم',
        'tomato_tomato_mosaic_virus': 'فيروس موزاييك الطماطم',
        'tomato_tomato_yellow_leaf_curl_virus': 'فيروس تجعد وإصفرار أوراق الطماطم',
        'wheat_aphid': 'من القمح',
        'wheat_black_rust': 'الصدأ الأسود في القمح',
        'wheat_blast': 'لفحة القمح',
        'wheat_brown_rust': 'الصدأ البني في القمح',
        'wheat_common_root_rot': 'تعفن جذور القمح الشائع',
        'wheat_fusarium_head_blight': 'لفحة السنبلة الفيوزارية في القمح',
        'wheat_healthy': 'قمح سليم',
        'wheat_leaf_blight': 'لفحة أوراق القمح',
        'wheat_mildew': 'البياض الدقيقي في القمح',
        'wheat_mite': 'سوس القمح',
        'wheat_septoria': 'سبتوريا القمح',
        'wheat_smut': 'تفحم القمح',
        'wheat_stem_fly': 'ذبابة ساق القمح',
        'wheat_tan_spot': 'البقعة السمراء في القمح',
        'wheat_yellow_rust': 'الصدأ الأصفر في القمح'
    }
    
    # Update diseases with Arabic names
    for disease in DiseaseType.objects.all():
        if disease.tag in arabic_names:
            disease.arabic_name = arabic_names[disease.tag]
            disease.save()

def reverse_migration(apps, schema_editor):
    DiseaseType = apps.get_model('core', 'DiseaseType')
    for disease in DiseaseType.objects.all():
        disease.arabic_name = None
        disease.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_diseasetype_arabic_name'),
    ]

    operations = [
        migrations.RunPython(add_arabic_names, reverse_migration),
    ]