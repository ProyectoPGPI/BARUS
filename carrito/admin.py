from django.contrib import admin

from carrito.models import Carrito, Direccion, ItemCarrito, Pedido

# Register your models here.
admin.site.register(Pedido)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Direccion)