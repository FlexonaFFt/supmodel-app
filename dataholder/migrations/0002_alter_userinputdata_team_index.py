# Generated by Django 5.0.6 on 2024-11-05 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataholder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinputdata',
            name='team_index',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
