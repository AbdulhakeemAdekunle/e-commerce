# Generated by Django 5.1.1 on 2024-10-07 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_rename_cart_id_cart_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'product')},
        ),
    ]
