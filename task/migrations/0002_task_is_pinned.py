# Generated by Django 4.2.21 on 2025-05-30 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
    ]
