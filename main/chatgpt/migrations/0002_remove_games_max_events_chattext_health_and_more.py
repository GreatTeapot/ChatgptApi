# Generated by Django 4.2.7 on 2023-12-25 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='games',
            name='max_events',
        ),
        migrations.AddField(
            model_name='chattext',
            name='health',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='chattext',
            name='hunger',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='chattext',
            name='thirst',
            field=models.IntegerField(default=100),
        ),
    ]