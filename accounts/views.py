from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import User, Account
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth import get_user_model
import os
from django.conf import settings

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
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
                username=username,
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_active = True
            user.save()

            # Crear cuenta asociada al usuario
            account = Account(user=user, address=address, telephone=telephone)
            
            # Manejar el avatar
            if not avatar:
                # El usuario no subió un avatar, usar el avatar por defecto
                default_avatar_path = os.path.join(settings.STATIC_ROOT, 'img', 'default_avatar.png')
                if not os.path.exists(default_avatar_path):
                    # Si el archivo por defecto no está en STATIC_ROOT, intentar con STATICFILES_DIRS
                    for static_dir in settings.STATICFILES_DIRS:
                        potential_path = os.path.join(static_dir, 'avatar', 'default_avatar.png')
                        if os.path.exists(potential_path):
                            default_avatar_path = potential_path
                            break
                
                # Asegurar que el directorio de destino exista
                avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
                os.makedirs(avatar_dir, exist_ok=True)
                
                # Generar un nombre de archivo único basado en el usuario
                user_avatar_filename = f"default_{user.id}.png"
                destination_path = os.path.join(avatar_dir, user_avatar_filename)
                
                # Copiar el avatar por defecto al directorio de medios con un nombre único
                with open(default_avatar_path, 'rb') as default_file:
                    with open(destination_path, 'wb') as dest_file:
                        dest_file.write(default_file.read())
                
                # Asignar la ruta relativa al campo avatar
                account.avatar = f'avatars/{user_avatar_filename}'
            else:
                account.avatar = avatar
            
            account.save()

            messages.success(request, '¡Registro exitoso! Puedes iniciar sesión.')
            return redirect('login')

        except IntegrityError:
            messages.error(request, 'El nombre de usuario o correo ya están en uso.')
        except Exception as e:
            # Capturar cualquier otra excepción que pueda ocurrir
            messages.error(request, f'Error durante el registro: {str(e)}')

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

def password_reset(request):
    """Vista para solicitar el restablecimiento de la contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generar token único para el usuario
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construir el enlace para restablecer la contraseña
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
            
            # Enviar correo electrónico
            subject = 'Restablece tu contraseña en SmitePRO'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': current_site.name,
            })
            
            send_mail(
                subject,
                message,
                'noreply@smitepro.com',  # Remitente
                [email],  # Destinatario
                fail_silently=False,
                html_message=message  # Permite contenido HTML en el correo
            )
            
            messages.success(request, 'Te hemos enviado un correo electrónico con instrucciones para restablecer tu contraseña.')
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            # No revelar si el email existe o no por seguridad
            messages.success(request, 'Te hemos enviado un correo electrónico con instrucciones para restablecer tu contraseña.')
            return redirect('password_reset_done')
    
    return render(request, 'accounts/password_reset_form.html')

def password_reset_done(request):
    """Vista que se muestra después de enviar el correo de restablecimiento"""
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Vista para confirmar el token y establecer una nueva contraseña"""
    try:
        # Decodificar el uid del usuario
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Verificar que el token sea válido
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if password != confirm_password:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'accounts/password_reset_confirm.html')
                
                # Cambiar la contraseña
                user.set_password(password)
                user.save()
                messages.success(request, 'Tu contraseña ha sido restablecida con éxito. Ahora puedes iniciar sesión.')
                return redirect('login')
            
            return render(request, 'accounts/password_reset_confirm.html')
        else:
            messages.error(request, 'El enlace de restablecimiento de contraseña ha expirado o no es válido.')
            return redirect('password_reset')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'El enlace de restablecimiento de contraseña ha expirado o no es válido.')
        return redirect('password_reset')

def password_reset_complete(request):
    """Vista para mostrar que el restablecimiento de contraseña se completó con éxito"""
    return render(request, 'accounts/password_reset_complete.html')



