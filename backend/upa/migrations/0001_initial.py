# Generated by Django 5.1 on 2024-08-17 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UPARegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Address')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='State')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='City')),
                ('pincode', models.CharField(blank=True, max_length=10, null=True, verbose_name='Pincode')),
                ('reference_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='Reference ID')),
            ],
        ),
    ]
