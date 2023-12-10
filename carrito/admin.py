from django.contrib import admin

from carrito.models import Carrito, Direccion, ItemCarrito, Pedido

from django.contrib import admin
from .models import Pedido
from .forms import PedidoAdminForm

class PedidoAdmin(admin.ModelAdmin):
    form = PedidoAdminForm
    readonly_fields = ['metodo_pago']

admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Direccion)