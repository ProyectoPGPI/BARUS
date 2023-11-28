from .models import  Producto

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test


#ESTO ES NUESTRO PROYECTO

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
    
###########################################################
#Vista para el carrito de la compra                       #
###########################################################
    
def mostrar_carrito(request):
    return render(request, 'carrito.html')

###########################################################
#Vistas para pago de clientes registrados / no registrados#
###########################################################

# Vista para usuarios autenticados
@login_required(login_url='/')
def pago_usuario_registrado(request):
    return render(request, 'pago_usuario_registrado.html')

# Vista para usuarios no autenticados
@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def pago_usuario_no_registrado(request):
    return render(request, 'pago_usuario_no_registrado.html')
