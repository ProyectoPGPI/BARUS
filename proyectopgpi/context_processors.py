from carrito.models import Carrito

def logueado_y_num_productos(request):
    context = {}

    logueado = request.user.is_authenticated

    cont = 0
    if request.user.is_authenticated:
        if Carrito.objects.filter(cliente_id=request.user.id).exists():
            carrito = Carrito.objects.get(cliente_id=request.user.id)
            cont = carrito.obtener_cantidad_total
    elif 'carrito_id' in request.session:
        carrito = Carrito.objects.get(id=request.session['carrito_id'])
        cont = carrito.obtener_cantidad_total

    context['logueado'] = logueado
    context['num_productos_carrito'] = cont
    return context
