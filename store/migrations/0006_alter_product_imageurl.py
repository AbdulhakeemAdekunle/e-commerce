# Generated by Django 5.1.1 on 2024-10-05 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_orderitem_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='imageurl',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
