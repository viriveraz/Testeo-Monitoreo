from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from camiones.models import Camion, AsignacionChofer

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('mostrar_mapa')  # Redirige a la página deseada
        else:
            messages.error(request, 'El usuario o la contraseña es incorrecto.')

    return render(request, 'autenticacion/login.html')


def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige a la página de login después del logout

def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'autenticacion/lista_usuarios.html', {'usuarios': usuarios})

def detalle_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    return render(request, 'autenticacion/detalle_usuario.html', {'usuario': usuario})