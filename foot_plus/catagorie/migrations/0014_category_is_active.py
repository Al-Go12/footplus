# Generated by Django 4.2.3 on 2023-11-29 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catagorie', '0013_alter_varients_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
