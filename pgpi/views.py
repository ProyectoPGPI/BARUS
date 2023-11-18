from django.http import HttpResponse, JsonResponse
from .models import Project, Task
from django.shortcuts import render

# Create your views here.
def index(request):
    title = 'Proyecto de PGPI!!'
    return render(request, 'index.html',{
        'title' : title
    })

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
