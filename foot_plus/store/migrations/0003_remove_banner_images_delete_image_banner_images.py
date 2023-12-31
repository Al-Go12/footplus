# Generated by Django 4.2.3 on 2023-11-20 09:53

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_image_banner_banner_name_banner_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='banner',
            name='images',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.AddField(
            model_name='banner',
            name='images',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('image1', 'Image 1'), ('image2', 'Image 2'), ('image3', 'Image 3')], max_length=15),
        ),
    ]
