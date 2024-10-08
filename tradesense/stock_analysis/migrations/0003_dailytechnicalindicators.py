# Generated by Django 4.2.15 on 2024-08-25 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stock_analysis", "0002_stock_industry"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyTechnicalIndicators",
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
                ("date", models.DateField()),
                ("rsi", models.JSONField(blank=True, null=True)),
                ("macd", models.JSONField(blank=True, null=True)),
                ("bollinger_bands", models.JSONField(blank=True, null=True)),
                ("sma", models.JSONField(blank=True, null=True)),
                ("ema", models.JSONField(blank=True, null=True)),
                ("stochastic", models.JSONField(blank=True, null=True)),
                ("atr", models.JSONField(blank=True, null=True)),
                ("obv", models.JSONField(blank=True, null=True)),
                ("fibonacci_retracement", models.JSONField(blank=True, null=True)),
                ("ichimoku_cloud", models.JSONField(blank=True, null=True)),
                ("parabolic_sar", models.JSONField(blank=True, null=True)),
                (
                    "stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="technical_indicators",
                        to="stock_analysis.stock",
                    ),
                ),
            ],
            options={
                "unique_together": {("stock", "date")},
            },
        ),
    ]
