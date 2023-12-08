from django.db import models
from catalogo.models import Producto
from django.contrib.auth.models import User

# Create your models here.

class Carrito(models.Model):
    cliente = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ItemCarrito')
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def calcular_total(self):
        total = sum(item.producto.precio * item.cantidad for item in self.itemcarrito_set.all())
        self.total = total
        self.save()
    
    def obtener_cantidad_total(self):
        return sum(item.cantidad for item in self.itemcarrito_set.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

class Direccion(models.Model):
    cliente = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=5)
    municipio = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)

class Pedido(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)

