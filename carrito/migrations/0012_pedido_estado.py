# Generated by Django 4.2.7 on 2023-12-09 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0011_remove_pedido_gastos_envio_carrito_gastos_envio'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='estado',
            field=models.CharField(choices=[('Aceptado', 'Aceptado'), ('En camino', 'En_camino'), ('Entregado', 'Entregado')], default='Aceptado', max_length=20),
        ),
    ]