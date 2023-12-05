from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from django.template import loader
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from django.shortcuts import redirect
from django.db.models import Q
from .models import Carrito, ItemCarrito
from django.db.models import Max

# Create your views here.

def carrito(request):
    context = {}
    context['usuario'] = request.user
    if(str(request.user) == 'AnonymousUser'):
        ultimo_carrito = Carrito.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
        Carrito.objects.filter(cliente_id=request.user.id).exclude(id=ultimo_carrito).delete()
        if 'carrito_id' not in request.session:
             carrito = Carrito.objects.get(cliente_id=request.user.id)
             carrito.productos.clear()
             carrito.calcular_total()
             carrito.save()
        context['carrito'] = Carrito.objects.get(cliente_id=request.user.id)
    else:
        if Carrito.objects.filter(cliente_id=request.user.id).exists():
            context['carrito'] = Carrito.objects.get(cliente_id=request.user.id)
    return render(request, 'carrito.html', context)
            

def actualizar_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cantidad = request.POST.get('cantidad')
        item_carrito = ItemCarrito.objects.get(pk=item_id)
        item_carrito.cantidad = cantidad
        item_carrito.save()

        item_carrito.carrito.calcular_total()

    return redirect('/carrito')

def borrar_del_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_carrito = ItemCarrito.objects.get(pk=item_id)
        item_carrito.delete()

        item_carrito.carrito.calcular_total()

    return redirect('/carrito')