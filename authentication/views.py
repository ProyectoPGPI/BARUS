from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from carrito.models import Carrito
from .models import Reclamacion 

from .forms import EmailAuthenticationForm

# Create your views here.

def contacto(request):
    return render(request, 'contacto.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        # Verificar si el correo electrónico ya está en uso
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo está ya en uso.')
            return render(request, 'signup.html')

        if password1 == password2:
            try:
                # Utiliza los campos del formulario personalizado
                user = User.objects.create_user(
                    username=username,
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=email,
                    password=password1
                )
                user.save()
                return redirect('login')
            
            except Exception as e:
                messages.error(request, f'Error creando el usuario: {str(e)}')
        else:
            messages.error(request, 'Las contraseñas no coinciden')

    # Si hay un error o la contraseña no coincide, permanece en la página de registro y conserva los datos del formulario.
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirigir a una página de éxito o a donde sea necesario
                return redirect('catalogo')  # Reemplaza 'dashboard' con el nombre de tu URL
    else:
        form = EmailAuthenticationForm()

    return render(request, 'login.html', {'form': form})

class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


def logout_view(request):
    response = redirect("/")
    if request.user.is_authenticated == True:
        logout(request)
        response.delete_cookie('token')
    return response

def reclamaciones(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        Reclamacion.objects.create(titulo=titulo, descripcion=descripcion, estado='Pendiente', usuario=request.user)
        return redirect('reclamaciones')  # Redirige para evitar reenvío del formulario al recargar la página

    reclamaciones = Reclamacion.objects.filter(usuario=request.user)
    return render(request, 'reclamaciones.html', {'reclamaciones': reclamaciones})