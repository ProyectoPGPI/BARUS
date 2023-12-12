from django.http import HttpResponse, JsonResponse

from django.template import loader
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.core.mail import send_mail

from django.shortcuts import redirect
from .models import Carrito, ItemCarrito, Pedido, Direccion, Producto
from django.db.models import Max
from django.db.models import F
from django.contrib.auth.decorators import login_required

from decimal import Decimal
import stripe
from django.shortcuts import render, redirect, reverse,\
    get_object_or_404
import random
import string
from django.contrib import messages


# Create your views here.

def carrito(request):
    context = {}
    context['usuario'] = request.user
    ultimo_carrito = Carrito.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
    ultima_direccion = Direccion.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
    if(str(request.user) == 'AnonymousUser'):
        if 'carrito_id' not in request.session:
            carrito = Carrito.objects.get(id = ultimo_carrito)
            carrito.productos.clear()
            carrito.calcular_total()
            carrito.save()
        context['carrito'] = Carrito.objects.get(id = ultimo_carrito)
        if 'direccion_data' in request.session:
            context['direccion'] = request.session['direccion_data']
    else:
        if Carrito.objects.filter(id = ultimo_carrito).exists():
            context['carrito'] = Carrito.objects.get(id = ultimo_carrito)
        if Direccion.objects.filter(id = ultima_direccion).exists():
            context['direccion'] = Direccion.objects.get(id = ultima_direccion)
    if 'carrito' not in context:
        context['boton'] = False
    return render(request, 'carrito.html', context)
            

def actualizar_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cantidad = request.POST.get('cantidad')
        item_carrito = ItemCarrito.objects.get(pk=item_id)
        
        item_carrito.cantidad = cantidad
        item_carrito.save()

        item_carrito.carrito.calcular_total()

        dic = request.session['stock_restante']
        dic[item_carrito.producto.id] = item_carrito.producto.stock - int(item_carrito.cantidad)
        request.session['stock_restante'] = dic

    return redirect('/carrito')

def borrar_del_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_carrito = ItemCarrito.objects.get(pk=item_id)
    
        
        item_carrito.delete()

        item_carrito.carrito.calcular_total()

        dic = request.session['stock_restante']
        dic[item_carrito.producto.id]= item_carrito.producto.stock
        request.session['stock_restante'] = dic

    return redirect('/carrito')

#Claves
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    if request.user.is_authenticated:
        ultimo_carrito = Carrito.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
        carrito_obj = Carrito.objects.get(id = ultimo_carrito)
        carrito_id = carrito_obj.id
    else:
        carrito_id = request.session.get('carrito_id', None)
    carrito = get_object_or_404(Carrito, id=carrito_id)
    carrito.calcular_total()

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', '')

        if metodo_pago == 'Contra reembolso':
            request.session['metodo_pago'] = metodo_pago
            # Llama a la función payment_completed directamente
            return payment_completed(request)
        else:
            request.session['metodo_pago'] = metodo_pago
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
            # redirect to Stripe payment form
            return redirect(session.url, code=303)
    else:
        return render(request,'carrito.html', locals())
    

def payment_completed(request):
    guardar_direccion = request.POST.get('guardar_direccion', 'off')
    if request.user.is_authenticated:
        ultimo_carrito = Carrito.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
        ultima_direccion = Direccion.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
        carro = Carrito.objects.get(id = ultimo_carrito)
        dire = Direccion.objects.get(id = ultima_direccion)
    else:
        carro = Carrito.objects.get(id = request.session['carrito_id'])
        direccion_data = request.session.get('direccion_data', None)

        if direccion_data:
            # Crea una instancia de Direccion
            dire = Direccion.objects.create(
                nombre=direccion_data['nombre'],
                apellidos=direccion_data['apellidos'],
                direccion=direccion_data['direccion'],
                codigo_postal=direccion_data['codigo_postal'],
                municipio=direccion_data['municipio'],
                provincia=direccion_data['provincia'],
                email=direccion_data['email'],
                telefono=direccion_data['telefono']
            )
    num_pedido = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    metodo_de_pago = request.session.get('metodo_pago')
    if carro.productos.exists():
        Pedido.objects.create(
            carrito = carro,
            direccion = dire,
            num_de_pedido=num_pedido,
            metodo_pago=metodo_de_pago
        )
    else:
        return redirect('/')
    if request.user.is_authenticated:
        Carrito.objects.create(cliente_id = request.user.id)
        if guardar_direccion == 'off':
            Direccion.objects.create(cliente_id = request.user.id)
        else:
            nueva_d = Direccion.objects.create(cliente_id = request.user.id)
            nueva_d.nombre = dire.nombre
            nueva_d.apellidos = dire.apellidos
            nueva_d.direccion = dire.direccion
            nueva_d.codigo_postal = dire.codigo_postal
            nueva_d.municipio = dire.municipio
            nueva_d.provincia = dire.provincia
            nueva_d.email = dire.email
            nueva_d.telefono = dire.telefono
            nueva_d.save()
            
    else:
        nuevo = Carrito.objects.create()
        request.session['carrito_id'] = nuevo.id
        
    enviar_correo_confirmacion(carro, dire)

    for item in carro.productos.all():
        cantidad = ItemCarrito.objects.get(carrito=carro, producto=item).cantidad
        p = Producto.objects.get(id = item.id)
        p.stock -= cantidad
        p.save()

    return render(request,'exito.html')

def enviar_correo_confirmacion(carrito, direccion):
    subject = 'Confirmación de pedido'

    # Obtén todos los pedidos asociados al carrito
    pedidos = Pedido.objects.filter(carrito=carrito)

    # Verifica si hay al menos un pedido
    if pedidos.exists():
        # Obtén el primer pedido (puedes ajustar esta lógica según tus necesidades)
        pedido = pedidos.first()

        # Construir el cuerpo del mensaje con los detalles del pedido
        message = f'Tu pedido ha sido confirmado. Detalles:\n\n'
        message += f'Número de seguimiento del pedido: {pedido.num_de_pedido}\n\n'  # Añade el número de pedido

        for item in carrito.itemcarrito_set.all():
            message += f'Producto: {item.producto.nombre}\n' + f'Cantidad: {item.cantidad}\n'
            message += f'Precio unitario: {item.producto.precio} EUR\n'

        message += f'Total del pedido: {carrito.total} EUR\n'
        message += f'Método de pago: {pedido.metodo_pago}\n\n' 

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
    else:
        # Manejar el caso donde no hay ningún pedido asociado al carrito
        # Puedes imprimir un mensaje de error o tomar otras acciones según sea necesario
        print("Error: No se encontró ningún pedido asociado al carrito.")


def payment_canceled(request):
    return render(request,'cancelado.html')

def direccion(request):
    context = {}
    if request.user.is_authenticated:
        ultima_direccion = Direccion.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
        if Direccion.objects.filter(id = ultima_direccion).exists():
            context['direccion'] = Direccion.objects.get(id = ultima_direccion)
    else:
        if 'direccion_data' in request.session:
            context['direccion'] = request.session['direccion_data']
    return render(request, 'direccion.html', context)

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
            ultima_direccion = Direccion.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
            if Direccion.objects.filter(id = ultima_direccion).exists():
                direccion_existente = Direccion.objects.get(id = ultima_direccion)
            else:
                direccion_existente = None

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

    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        # Filtrar los pedidos asociados al usuario autenticado
        context['pedidos'] = Pedido.objects.filter(direccion__cliente=request.user)
    else:
        # Si el usuario no está autenticado, establecer una lista vacía de pedidos
        context['pedidos'] = []

    return render(request, 'mis_pedidos.html', context)

def buscar_pedidos(request):
    numero_pedido = request.GET.get('numero_pedido', '')
    
    if request.user.is_authenticated:
        pedidos = Pedido.objects.filter(direccion__cliente=request.user, num_de_pedido__icontains=numero_pedido)
    else:
        if numero_pedido:
            pedidos = Pedido.objects.filter(direccion__cliente__isnull=True, num_de_pedido__icontains=numero_pedido)
        else:
            pedidos = []

    return render(request, 'mis_pedidos.html', {'pedidos': pedidos, 'numero_pedido': numero_pedido})