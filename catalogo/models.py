from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import os


class TipoSeccion(models.TextChoices):
    GENERAL = 'general', _('General')
    INTERIOR = 'interior', _('Interior')
    EXTERIOR = 'exterior', _('Exterior')
    MAQUINARIA = 'maquinaria', _('Maquinaria')

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion=models.TextField()
    tipo_seccion = models.CharField(max_length=10,choices=TipoSeccion.choices,default=TipoSeccion.GENERAL)
    imagen = models.ImageField(upload_to="" ,null=True, blank=True)
    departamento = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=50)
    stock = models.IntegerField(default= 0)
    
    def __str__(self):
        return self.nombre
    
class Opinion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"
    
