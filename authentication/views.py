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

from .forms import EmailAuthenticationForm, ReclamacionForm

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
        # Utiliza EmailAuthenticationForm
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Utiliza authenticate correctamente para comparar el campo de correo electrónico
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('catalogo') 
                
            else:
                messages.error(request, 'Credenciales inválidas. Por favor, verifica tu correo y contraseña.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
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

        # Validar longitud del título y descripción
        if len(titulo) > 20:
            messages.error(request, 'La longitud del título debe ser de 20 caracteres como máximo.')
        elif len(descripcion) > 255:
            messages.error(request, 'La longitud de la descripción debe ser de 255 caracteres como máximo.')
        else:
            # Crear la reclamación si la validación pasa
            Reclamacion.objects.create(titulo=titulo, descripcion=descripcion, estado='Pendiente', usuario=request.user)
            return redirect('reclamaciones')

    reclamaciones = Reclamacion.objects.filter(usuario=request.user)
    return render(request, 'reclamaciones.html', {'reclamaciones': reclamaciones})