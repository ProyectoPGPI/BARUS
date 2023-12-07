from .models import  Producto

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import get_object_or_404, redirect
from .models import Producto
from carrito.models import Carrito, ItemCarrito

def contacto(request):
    return render(request, 'contacto.html')

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

    cont = 0
    if request.user.is_authenticated:
        if Carrito.objects.filter(cliente_id=request.user.id).exists():
            carrito = Carrito.objects.get(cliente_id = request.user.id)
            cont = carrito.obtener_cantidad_total
    else:
        if 'carrito_id' in request.session:
            carrito = Carrito.objects.get(id = request.session['carrito_id'])
            cont = carrito.obtener_cantidad_total
    logueado = False
    if request.user.is_authenticated:
        logueado = True

    context['logueado'] = logueado     
    context['num_productos_carrito'] = cont
    return render(request, 'catalogo.html', context)

def product_view(request, product_id):
    context = {}
    producto = Producto.objects.get(id=product_id)
    context['producto'] = producto
    if request.user.is_authenticated:
        if Carrito.objects.filter(cliente_id=request.user.id).exists():
            carrito = Carrito.objects.get(cliente_id = request.user.id)
            cont = carrito.obtener_cantidad_total
    else:
        if 'carrito_id' in request.session:
            carrito = Carrito.objects.get(id = request.session['carrito_id'])
            cont = carrito.obtener_cantidad_total
    context['num_productos_carrito'] = cont
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


def agregar_al_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = 1

        if request.user.is_authenticated:
            # Usuario autenticado, usar base de datos
            usuario = request.user
            carrito, created = Carrito.objects.get_or_create(cliente=usuario)
        else:
            # Usuario no autenticado, usar sesión
            if 'carrito_id' not in request.session:
                carrito = Carrito.objects.create()
                request.session['carrito_id'] = carrito.id
            else:
                carrito_id = request.session['carrito_id']
                carrito = get_object_or_404(Carrito, id=carrito_id)

        producto = get_object_or_404(Producto, pk=producto_id)

        # Verificar si el producto ya está en el carrito
        item_carrito, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 1}  # Establecer la cantidad a 1 si es la primera vez que se agrega
        )

        # Si el producto ya está en el carrito, incrementar la cantidad
        if not item_created:
            item_carrito.cantidad += cantidad
            item_carrito.save()

        # Calcular el total del carrito
        carrito.calcular_total()

        # Redirigir a la página principal o a la página del carrito
        return redirect('/')  # Puedes cambiar esto a la URL de la página del carrito

    return redirect('/')
    
