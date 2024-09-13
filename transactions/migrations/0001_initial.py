# Generated by Django 5.1.1 on 2024-09-13 06:50

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_amount",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                (
                    "balance_after_transaction",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                ("transaction_description", models.CharField(max_length=20)),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("DE", "Deposit"), ("WI", "Withdrawal")],
                        default="DE",
                        max_length=2,
                    ),
                ),
                ("transaction_method", models.CharField(max_length=20)),
                (
                    "transaction_datetime",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "account_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="accounts.accountmodel",
                    ),
                ),
            ],
        ),
    ]
