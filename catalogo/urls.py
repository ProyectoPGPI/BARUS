from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [

    path('', views.index),
    path('catalogo/',views.catalogo),
    path('buscar/', buscar_producto, name='buscar_producto'),
    path('resultados_busqueda/', mostrar_resultados_busqueda, name='resultados_busqueda'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)