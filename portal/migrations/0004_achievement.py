# Generated by Django 5.1.5 on 2025-01-24 02:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_budget_fundraising_expenditure_financialsummary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('achievement_type', models.CharField(choices=[('Student', 'Student'), ('Faculty', 'Faculty'), ('Department', 'Department')], max_length=20)),
                ('awarded_to', models.CharField(help_text='Name of the recipient or department', max_length=200)),
                ('date_awarded', models.DateField(default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to='achievements/')),
            ],
        ),
    ]
