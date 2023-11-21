from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    Project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' - Projecto: ' + self.Project.name
    
#ESTO ES NUESTRO PROYECTO:

class TipoCategoria(models.TextChoices):
    GENERAL = 'general', _('General')
    INTERIOR = 'interior', _('Interior')
    EXTERIOR = 'exterior', _('Exterior')
    MAQUINARIA = 'maquinaria', _('Maquinaria')

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion=models.TextField()
    fecha_registro=models.DateField()
    tipo_categoria = models.CharField(max_length=10,choices=TipoCategoria.choices,default=TipoCategoria.GENERAL)
    imagen = models.ImageField(upload_to="productos/",null=True, blank=True)
    avalible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
