from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse

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
                return HttpResponse('User created successfully')
            except Exception as e:
                return HttpResponse(f'Error creating user: {str(e)}')

        return HttpResponse('Passwords do not match')

    return HttpResponse('Invalid request method')