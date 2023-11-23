from django.http import HttpResponse, JsonResponse
from .models import  Producto, TipoSeccion
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.db.models import Q


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

###################################################################################
#Función para buscar productos por nombre, descripción, departamento o fabricante.#
###################################################################################

def buscar_producto(request):
    busqueda = request.GET.get('Buscar')
    productos = Producto.objects.all()

    if busqueda is not None:
        productos = Producto.objects.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda) | Q(departamento__icontains=busqueda) | Q(fabricante__icontains=busqueda))
    else: 
        return redirect('catalogo')
    
    return render(request, 'catalogo.html', {'productos': productos})


####################################################
#Función para mostrar los productos de la búsqueda.#
####################################################

def mostrar_resultados_busqueda(request):
    busqueda = request.GET.get('Buscar', '').strip()

    if busqueda:  
        productos = Producto.objects.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda) | Q(departamento__icontains=busqueda) | Q(fabricante__icontains=busqueda))
        return render(request, 'busqueda_resultados.html', {'productos': productos, 'busqueda': busqueda})
    else:
        return redirect('catalogo')