from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('about/',views.about),
    path('hello/<str:username>', views.hello), 
    path('projects/',views.projects),
    path('tasks/',views.tasks),
    #Esto es nuestro proyecto:
    path('', views.index),
    path('catalogo/',views.catalogo)
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)