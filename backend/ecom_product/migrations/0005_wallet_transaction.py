# Generated by Django 5.1 on 2025-04-13 12:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_product', '0004_alter_cartitem_status_payment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default='0.00', max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('credited', 'Credited'), ('debited', 'Debited')], max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='ecom_product.wallet')),
            ],
        ),
    ]
