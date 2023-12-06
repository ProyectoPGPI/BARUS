from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test

from django.shortcuts import get_object_or_404, redirect
from .models import Producto
from carrito.models import Carrito, ItemCarrito
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

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
    cont = 0
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
    

# Método para usuarios registrados y no registrados
def procesar_pago(request):
    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        # Usuario autenticado: Obtener o crear el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(cliente=request.user)
        # Obtener los productos en el carrito
        productos_en_carrito = carrito.itemcarrito_set.all()
        # Configurar el email del cliente para Stripe
        customer_email = request.user.email
    else:
        # Usuario no autenticado: Obtener o crear el carrito de la sesión
        if 'carrito_id' not in request.session:
            carrito = Carrito.objects.create()
            request.session['carrito_id'] = carrito.id
        else:
            carrito_id = request.session['carrito_id']
            carrito = get_object_or_404(Carrito, id=carrito_id)
        # Obtener los productos en el carrito
        productos_en_carrito = carrito.itemcarrito_set.all()
        # Configurar el email del cliente para Stripe como None
        customer_email = None

    # Calcular el total del carrito
    total_del_carrito = sum(item.producto.precio * item.cantidad for item in productos_en_carrito)

   # Crear una sesión de pago en Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        customer_email=customer_email,
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.producto.nombre,
                    },
                    'unit_amount': int(item.producto.precio * 100),
                },
                'quantity': item.cantidad,
            } for item in productos_en_carrito
        ],
        mode='payment',
        success_url=request.build_absolute_uri('/exito/'),
        cancel_url=request.build_absolute_uri('/cancelado/'),
    )
    
    # Renderizar la página de pago
    template_name = 'pago_usuario_registrado.html' if request.user.is_authenticated else 'pago_usuario_no_registrado.html'
    return render(request, template_name, {'session': session, 'productos_en_carrito': productos_en_carrito, 'total_del_carrito': total_del_carrito})

# Vista para usuarios registrados
@login_required(login_url='/login/')
def pago_usuario_registrado(request):
    return procesar_pago(request)

# Vista para usuarios no autenticados
@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def pago_usuario_no_registrado(request):
    return procesar_pago(request)

def exito(request):
    return render(request, 'exito.html')

def cancelado(request):
    return render(request, 'cancelado.html')