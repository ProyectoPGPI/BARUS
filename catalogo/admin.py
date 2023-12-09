from django.contrib import admin

from authentication.models import Reclamacion
from .models import Opinion, Producto

# Register your models here.
admin.site.register(Producto)
admin.site.register(Reclamacion)
admin.site.register(Opinion)