# Generated by Django 4.2.3 on 2023-11-20 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_image', models.ImageField(blank=True, upload_to='banner_images/')),
            ],
        ),
        migrations.AddField(
            model_name='banner',
            name='banner_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='banner',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='banner',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='banners', to='store.image'),
        ),
    ]
