# Generated by Django 5.1 on 2025-06-22 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_incomesetting'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeSettingForWomenOld',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, choices=[('N/A', 'N/A'), ('BPL', 'BPL'), ('Handicap', 'Handicap'), ('Child Below 18', 'Child Below 18'), ('Mature Female', 'Mature Female'), ('Senior Citizen', 'Senior Citizen')], max_length=15, null=True)),
                ('income', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('previous_income_for_women_old', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
            ],
        ),
    ]
