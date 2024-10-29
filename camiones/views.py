import json
import requests
from django.http import JsonResponse
from .models import Camion, AsignacionChofer
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import UsuarioForm, CamionForm, AsignacionChoferForm

# Obtener ubicación del camión
def obtener_ubicacion(request, camion_id):
    try:
        camion = Camion.objects.get(id=camion_id)
        return JsonResponse({
            'latitud': camion.latitud,
            'longitud': camion.longitud
        })
    except Camion.DoesNotExist:
        return JsonResponse({'error': 'Camión no encontrado'}, status=404)

def mostrar_mapa(request):
    return render(request, 'mapa.html')

@csrf_exempt
def actualizar_ubicacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            latitud = data.get('latitud')
            longitud = data.get('longitud')

            # Validar que todos los datos estén presentes
            if not nombre or latitud is None or longitud is None:
                return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)

            # Obtener el primer camión con el nombre dado o crear uno si no existe
            dispositivo = Camion.objects.filter(nombre=nombre).first()
            if dispositivo is None:
                dispositivo = Camion.objects.create(nombre=nombre)

            # Asignar los valores de latitud y longitud
            dispositivo.latitud = latitud
            dispositivo.longitud = longitud
            dispositivo.ultima_actualizacion = timezone.now()
            dispositivo.save()

            return JsonResponse({'status': 'Ubicación actualizada'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def dispositivos_admin_view(request):
    dispositivos_conectados = Camion.objects.filter(ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5))
    return render(request, 'dispositivos_admin.html', {'dispositivos': dispositivos_conectados})

@login_required
def dispositivos_chofer_view(request):
    dispositivo = Camion.objects.get(nombre=request.user.username)
    return render(request, 'dispositivos_chofer.html', {'dispositivo': dispositivo})

@login_required
def obtener_ubicaciones(request):
    dispositivos_conectados = Camion.objects.filter(ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5))
    data = [{'nombre': dispositivo.nombre, 'latitud': dispositivo.latitud, 'longitud': dispositivo.longitud} for dispositivo in dispositivos_conectados]
    return JsonResponse({'dispositivos': data})

# Redirección tras el login
@login_required
def redirigir_seleccion_camion(request):
    print(f"Usuario autenticado: {request.user}")
    camion_asignado = Camion.objects.filter(conductor=request.user).first()
    if camion_asignado:
        print(f"Camión asignado: {camion_asignado}")
        return redirect('vista_conductor')  # Redirige a la vista de conductor
    else:
        print("No hay camión asignado, redirigiendo a la selección.")
        return redirect('seleccionar_camion')  # Redirige a la selección de camión


# Vista para seleccionar camión
@login_required
def seleccionar_camion(request):
    camiones_disponibles = Camion.objects.filter(conductor__isnull=True)  # Camiones sin conductor asignado
    if request.method == 'POST':
        camion_id = request.POST.get('camion_id')
        camion = get_object_or_404(Camion, id=camion_id)
        # Asignamos el camión seleccionado al conductor
        camion.conductor = request.user
        camion.save()
        return redirect('vista_conductor')  # Redirige a la vista donde el conductor puede ver su camión
    return render(request, 'seleccionar_camion.html', {'camiones': camiones_disponibles})

# Vistas para usuarios
def usuarios_list(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})

def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuario_form.html', {'form': form})

def usuario_update(request, id):
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario_form.html', {'form': form})

def usuario_delete(request, id):
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuarios_list')
    return render(request, 'usuario_confirm_delete.html', {'usuario': usuario})

# Vistas para camiones
def camiones_list(request):
    camiones = Camion.objects.all()
    return render(request, 'camiones_list.html', {'camiones': camiones})

def camion_create(request):
    if request.method == 'POST':
        form = CamionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('camiones_list')
    else:
        form = CamionForm()
    return render(request, 'camion_form.html', {'form': form})

def camion_update(request, id):
    camion = get_object_or_404(Camion, id=id)
    if request.method == 'POST':
        form = CamionForm(request.POST, instance=camion)
        if form.is_valid():
            form.save()
            return redirect('camiones_list')
    else:
        form = CamionForm(instance=camion)
    return render(request, 'camion_form.html', {'form': form})

def camion_delete(request, id):
    camion = get_object_or_404(Camion, id=id)
    if request.method == 'POST':
        camion.delete()
        return redirect('camiones_list')
    return render(request, 'camion_confirm_delete.html', {'camion': camion})

# Vista para asignar conductor a un camión
def asignar_conductor(request):
    if request.method == 'POST':
        form = AsignacionChoferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('camiones_list')
    else:
        form = AsignacionChoferForm()
    return render(request, 'asignar_conductor_form.html', {'form': form})
