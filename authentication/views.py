from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib import messages

from .forms import EmailAuthenticationForm

# Create your views here.

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                # Utiliza los campos del formulario personalizado
                user = User.objects.create_user(
                    username=username,
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST['email'],
                    password=password1
                )
                user.save()
                return redirect('login')
            
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Passwords do not match')

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