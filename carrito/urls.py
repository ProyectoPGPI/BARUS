from django.urls import include, path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('carrito',views.carrito, name='carrito'),
    path('actualizar_carrito/', actualizar_carrito, name='actualizar_carrito'),
    path('borrar_del_carrito/', borrar_del_carrito, name='borrar_del_carrito'),
    path('carrito/', views.payment_process, name='carrito'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    path('direccion/', views.direccion, name = 'direccion'),
    path('crear_direccion/', crear_direccion, name='crear_direccion'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
]