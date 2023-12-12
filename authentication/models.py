from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Reclamacion(models.Model):
    ESTADOS = (
        ('Pendiente', 'Pendiente'),
        ('Revisada', 'Revisada'),
        ('Cancelada', 'Cancelada'),
    )

    titulo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo