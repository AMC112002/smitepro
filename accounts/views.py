from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import User, Account
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Ahora se ingresa un username
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        avatar = request.FILES.get('avatar')  # Recibe el archivo de imagen si se sube

        # Verificar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        try:
            user = User.objects.create_user(
                username=username,  # Ahora usa el username ingresado
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_active = True
            user.save()

            account = Account(user=user, address=address, telephone=telephone, avatar=avatar)
            account.save()

            messages.success(request, '¡Registro exitoso! Puedes iniciar sesión.')
            return redirect('login')

        except IntegrityError:
            messages.error(request, 'El nombre de usuario o correo ya están en uso.')

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Cambiado a `identifier`
        password = request.POST['password']
        
        # Buscar usuario por nombre de usuario o correo electrónico
        user = User.objects.filter(username=identifier).first() or User.objects.filter(email=identifier).first()
        
        # Autenticar usuario
        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None and user.is_active:
                auth_login(request, user)
                messages.success(request, 'Has iniciado sesión correctamente')
                return redirect('success')
            else:
                messages.error(request, 'Your account is not active. Please wait for admin approval.')
        else:
            messages.error(request, 'Usuario/email o contraseña incorrectos.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.\n Hasta pronto.')
    return redirect('home')

@login_required
def success(request):
    return redirect('home')

@login_required
def perfil(request):
    return render(request, "accounts/perfil.html")



