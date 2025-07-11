# Generated by Django 5.1 on 2025-06-22 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_legincomemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child_one', models.CharField(blank=True, choices=[('Normal', 'Normal'), ('BPL', 'BPL'), ('Handicap', 'Handicap')], max_length=15, null=True)),
                ('child_two', models.CharField(blank=True, choices=[('Normal', 'Normal'), ('BPL', 'BPL'), ('Handicap', 'Handicap')], max_length=15, null=True)),
                ('child_three', models.CharField(blank=True, choices=[('Normal', 'Normal'), ('BPL', 'BPL'), ('Handicap', 'Handicap')], max_length=15, null=True)),
                ('income', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('previous_income', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
            ],
        ),
    ]
