from django.http import HttpResponse, JsonResponse

from django.template import loader
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.core.mail import send_mail

from django.shortcuts import redirect
from .models import Carrito, ItemCarrito, Pedido, Direccion
from django.db.models import Max
from django.db.models import F

from decimal import Decimal
import stripe
from django.shortcuts import render, redirect, reverse,\
    get_object_or_404

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
        if 'direccion_data' in request.session:
            context['direccion'] = request.session['direccion_data']
    else:
        if Carrito.objects.filter(cliente_id=request.user.id).exists():
            context['carrito'] = Carrito.objects.get(cliente_id=request.user.id)
        if Direccion.objects.filter(cliente_id=request.user.id).exists():
            context['direccion'] = Direccion.objects.get(cliente_id = request.user.id)
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

#Claves
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    if request.user.is_authenticated:
        carrito_obj = Carrito.objects.get(cliente_id=request.user.id)
        carrito_id = carrito_obj.id
    else:
        carrito_id = request.session.get('carrito_id', None)
    carrito = get_object_or_404(Carrito, id=carrito_id)
    carrito.calcular_total()
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('completed'))
        cancel_url = request.build_absolute_uri(reverse('canceled'))
    # Stripe checkout session data
        session_data = {
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
    # add order items to the Stripe checkout session
        for item in carrito.itemcarrito_set.all():
            session_data['line_items'].append({
                'price_data': {
                'unit_amount': int(item.producto.precio * float(Decimal('100'))),
                'currency': 'eur',
                'product_data': {
                    'name': item.producto.nombre,
                },
            },
                'quantity': item.cantidad,
            })
        # Agregar los gastos de envío como un ítem separado
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(carrito.gastos_envio * float(Decimal('100'))),
                'currency': 'eur',
                'product_data': {
                    'name': 'Gastos de Envío',
                },
            },
            'quantity': 1,
        })
        # create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        print(session)
        # redirect to Stripe payment form
        return redirect(session.url, code=303)
    else:
        return render(request,'carrito.html', locals())
    

def payment_completed(request):
    if request.user.is_authenticated:
        carro = Carrito.objects.get(cliente_id = request.user.id)
        dire = Direccion.objects.get(cliente_id = request.user.id)
    else:
        carro = Carrito.objects.get(id = request.session['carrito_id'])
        dire = Carrito.objects.get(id = request.session['direccion_data'])
    Pedido.objects.create(
        carrito = carro,
        direccion = dire
    )

    enviar_correo_confirmacion(carro, dire)

    mis_pedidos(request)
    return redirect('mis_pedidos')

def enviar_correo_confirmacion(carrito, direccion):
    subject = 'Confirmación de pedido'
    
    # Construir el cuerpo del mensaje con los detalles del pedido
    message = f'Tu pedido ha sido confirmado. Detalles:\n\n'
    
    for item in carrito.itemcarrito_set.all():
        message += f'Producto: {item.producto.nombre}\n' + f'Cantidad: {item.cantidad}\n'
        message += f'Precio unitario: {item.producto.precio} EUR\n'
        message += f'Precio unitario: {item.gastos_envio} EUR\n'
    
    message += f'Total del pedido: {carrito.total} EUR\n\n'
    
    message += f'Dirección de entrega:\n'
    message += f'Nombre: {direccion.nombre} {direccion.apellidos}\n'
    message += f'Dirección: {direccion.direccion}\n'
    message += f'Código Postal: {direccion.codigo_postal}\n'
    message += f'Municipio: {direccion.municipio}\n'
    message += f'Provincia: {direccion.provincia}\n'
    message += f'Email: {direccion.email}\n'
    message += f'Teléfono: {direccion.telefono}\n'

    # Enviar el correo electrónico
    send_mail(subject, message, 'baruspgpi@gmail.com', [direccion.email])

def payment_canceled(request):
    return render(request,'cancelado.html')

def direccion(request):
    return render(request, 'direccion.html')

def crear_direccion(request):
    if request.method == 'POST':
        # Recupera los datos del formulario
        nombre = request.POST['nombre']
        apellidos = request.POST['apellidos']
        direccion = request.POST['direccion']
        codigo_postal = request.POST['codigo_postal']
        municipio = request.POST['municipio']
        provincia = request.POST['provincia']
        email = request.POST['email']
        telefono = request.POST['telefono']

        # Crea una instancia de Direccion y guarda en la base de datos
        if request.user.is_authenticated:
            direccion_existente = Direccion.objects.filter(cliente=request.user).first()

            if direccion_existente:
                # Si la dirección existe, actualiza los campos
                direccion_existente.nombre = nombre
                direccion_existente.apellidos = apellidos
                direccion_existente.direccion = direccion
                direccion_existente.codigo_postal = codigo_postal
                direccion_existente.municipio = municipio
                direccion_existente.provincia = provincia
                direccion_existente.email = email
                direccion_existente.telefono = telefono
                direccion_existente.save()
            else:
                # Si la dirección no existe, crea una nueva
                Direccion.objects.create(
                    cliente=request.user,
                    nombre=nombre,
                    apellidos=apellidos,
                    direccion=direccion,
                    codigo_postal=codigo_postal,
                    municipio=municipio,
                    provincia=provincia,
                    email=email,
                    telefono=telefono
                )
        else:
            # Si no está autenticado, guarda la información en la sesión
            direccion_data = {
                'nombre': nombre,
                'apellidos': apellidos,
                'direccion': direccion,
                'codigo_postal': codigo_postal,
                'municipio': municipio,
                'provincia': provincia,
                'email': email,
                'telefono': telefono
            }

            # Almacena la información en la sesión
            request.session['direccion_data'] = direccion_data

        return carrito(request)

    return redirect('/carrito/')

def mis_pedidos(request):
    context = {}
    context['pedidos'] = Pedido.objects.filter(direccion__cliente = request.user)
    return render(request, 'mis_pedidos.html', context)