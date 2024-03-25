# Generated by Django 3.2.24 on 2024-03-25 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twilioService', '0002_auto_20240324_2200'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sms_message_sid', models.CharField(max_length=34, unique=True)),
                ('sms_sid', models.CharField(max_length=34)),
                ('wa_id', models.CharField(max_length=20)),
                ('num_media', models.CharField(max_length=3)),
                ('profile_name', models.CharField(blank=True, max_length=100, null=True)),
                ('message_type', models.CharField(max_length=10)),
                ('sms_status', models.CharField(max_length=20)),
                ('body', models.TextField()),
                ('to_number', models.CharField(max_length=30)),
                ('from_number', models.CharField(max_length=30)),
                ('num_segments', models.CharField(max_length=3)),
                ('referral_num_media', models.CharField(blank=True, max_length=3, null=True)),
                ('message_sid', models.CharField(max_length=34)),
                ('account_sid', models.CharField(max_length=34)),
                ('api_version', models.CharField(max_length=10)),
            ],
        ),
    ]
