from django.http import HttpResponse, JsonResponse
from .models import Project, Task, Producto, TipoCategoria
from django.shortcuts import render

# Create your views here.
#ESTAS SON FUNCIONES DE EJEMPLO
def hello(request,username):
    print(username)
    return HttpResponse("<h2>Hello %s</h2>" %username)

def about(request):
    username='carnucbol'
    return render(request,'about.html',{'username':username})

def projects(request):
    #projects=list(Project.objects.values())
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})

def tasks(request):
    tasks = Task.objects.all()
    return render(request, 'tasks.html', {'tasks':tasks})
    #return HttpResponse('task: %s' % task.title)

#ESTO ES NUESTRO PROYECTO

def index(request):
    title = 'Proyecto de PGPI!!'
    return render(request, 'index.html',{
        'title' : title
    })


def catalogo(request):
    productos_por_categoria = {}
    categorias = TipoCategoria.choices

    for categoria in categorias:
        if categoria[0] == 'general':
            productos_por_categoria[categoria[1]] = Producto.objects.all()
        else:
            productos_por_categoria[categoria[1]] = Producto.objects.filter(tipo_categoria=categoria[0])

    return render(request, 'catalogo.html', {'productos_por_categoria': productos_por_categoria})
