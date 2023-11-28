from django.db import models
from catalogo.models import Producto
from django.contrib.auth.models import User

# Create your models here.

class Carrito(models.Model):
    productos = models.ManyToManyField(Producto, through='ItemCarrito')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def calcularTotal(self):
        total = sum(item.producto.precio * item.cantidad for item in self.itemcarrito_set.all())
        self.total = total
        self.save()
        
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)