# Generated by Django 4.2.7 on 2023-12-08 19:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0007_merge_0003_direccion_pedido_0006_carrito_gastos_envio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carrito',
            name='gastos_envio',
        ),
    ]
