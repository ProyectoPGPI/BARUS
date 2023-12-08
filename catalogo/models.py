from django.db import models
from django.utils.translation import gettext_lazy as _

class TipoSeccion(models.TextChoices):
    GENERAL = 'general', _('General')
    INTERIOR = 'interior', _('Interior')
    EXTERIOR = 'exterior', _('Exterior')
    MAQUINARIA = 'maquinaria', _('Maquinaria')

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion=models.TextField()
    fecha_registro=models.DateField()
    tipo_seccion = models.CharField(max_length=10,choices=TipoSeccion.choices,default=TipoSeccion.GENERAL)
    imagen = models.ImageField(upload_to="productos/",null=True, blank=True)
    avalible = models.BooleanField(default=True)
    departamento = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=50)
    stock = models.IntegerField(default= 0)
    
    def __str__(self):
        return self.nombre
    
#Este es el comentario para el gitignore