from django.urls import include, path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('carrito',views.carrito, name='carrito'),
    path('actualizar_carrito/', actualizar_carrito, name='actualizar_carrito'),
    path('borrar_del_carrito/', borrar_del_carrito, name='borrar_del_carrito'),
]