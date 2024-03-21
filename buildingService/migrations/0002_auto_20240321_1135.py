# Generated by Django 3.2.24 on 2024-03-21 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildingService', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressAbbreviation',
            fields=[
                ('primary_key', models.AutoField(primary_key=True, serialize=False)),
                ('standard_abbreviation', models.CharField(max_length=10, unique=True)),
                ('common_forms', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='building',
            name='address_normalized',
            field=models.TextField(editable=False),
        ),
    ]
