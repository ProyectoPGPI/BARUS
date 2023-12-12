from carrito.models import Carrito
from django.db.models import Max

def logueado_y_num_productos(request):
    context = {}

    logueado = request.user.is_authenticated
    ultimo_carrito = Carrito.objects.filter(cliente_id=request.user.id).aggregate(Max('id'))['id__max']
    cont = 0
    if request.user.is_authenticated:
        if Carrito.objects.filter(id = ultimo_carrito).exists():
            carrito = Carrito.objects.get(id = ultimo_carrito)
            cont = carrito.obtener_cantidad_total
    elif 'carrito_id' in request.session:
        carrito = Carrito.objects.get(id = ultimo_carrito)
        cont = carrito.obtener_cantidad_total

    context['logueado'] = logueado
    context['num_productos_carrito'] = cont
    return context
