from django.urls import include, path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('',views.catalogo, name='catalogo'),
    path('producto/<int:product_id>', views.product_view),
    path('buscar/', buscar_producto, name='buscar_producto'),

    path('resultados_busqueda/', mostrar_resultados_busqueda, name='resultados_busqueda'),
    path('agregar_al_carrito/', agregar_al_carrito, name='agregar_al_carrito'),    
    path('procesar_pago/', views.procesar_pago, name='pagar'), 
    path('exito/', exito, name='exito'),
    path('cancelado/', cancelado, name='cancelado'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)