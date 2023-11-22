from django.http import HttpResponse, JsonResponse
from .models import  Producto, TipoSeccion
from django.shortcuts import render



#ESTO ES NUESTRO PROYECTO

def index(request):
    title = 'Proyecto de PGPI!!'
    return render(request, 'index.html',{
        'title' : title
    })


def catalogo(request):
    productos_por_seccion = {}
    secciones = TipoSeccion.choices

    for seccion in secciones:
        if seccion[0] == 'general':
            productos_por_seccion[seccion[1]] = Producto.objects.all()
        else:
            productos_por_seccion[seccion[1]] = Producto.objects.filter(tipo_seccion=seccion[0])

    return render(request, 'catalogo.html', {'productos_por_seccion': productos_por_seccion})