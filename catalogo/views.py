from django.http import HttpResponse, JsonResponse
from .models import  Producto, TipoSeccion
from django.shortcuts import render
from django.template import loader
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404



#ESTO ES NUESTRO PROYECTO

def index(request):
    title = 'Proyecto de PGPI!!'
    return render(request, 'index.html',{
        'title' : title
    })


def catalogo(request):
    context = {}
    opcion_seleccionada = 'general'

    if request.method == 'POST':
        # Obtén el valor seleccionado del menú desplegable
        opcion_seleccionada = request.POST.get('opcion')

    if(opcion_seleccionada!=None):
        if opcion_seleccionada == 'general':
            context['productos'] = Producto.objects.all()
        else:
            context['productos'] = Producto.objects.filter(tipo_seccion=opcion_seleccionada)
    context['opcion_seleccionada'] = opcion_seleccionada
    return render(request, 'catalogo.html', context)

def product_view(request, product_id):
    context = {}
    producto = Producto.objects.get(id=product_id)
    context['producto'] = producto
    return render(request, 'producto.html', context)