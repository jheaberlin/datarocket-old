# Generated by Django 4.1.5 on 2023-01-31 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datarocket', '0005_alter_batch_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]