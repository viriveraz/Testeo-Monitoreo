import json
import requests
from django.http import JsonResponse
from .models import Camion
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required

# Obtener ubicación del camión
def obtener_ubicacion(request, camion_id):
    try:
        camion = Camion.objects.get(id=camion_id)
        # Retornamos la ubicación del camión en formato JSON
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

            # Imprimir los datos recibidos para verificar
            print(f"Datos recibidos: nombre={nombre}, latitud={latitud}, longitud={longitud}")

            # Validar que todos los datos estén presentes
            if not nombre or latitud is None or longitud is None:
                print("Error: Faltan datos en la solicitud")
                return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)

            # Buscar si el dispositivo con ese nombre ya existe, o crearlo si no existe
            dispositivo, creado = Camion.objects.get_or_create(nombre=nombre)

            # Asignar los valores de latitud y longitud
            dispositivo.latitud = latitud
            dispositivo.longitud = longitud
            dispositivo.ultima_actualizacion = timezone.now()
            dispositivo.save()

            print(f"Ubicación de {nombre} actualizada correctamente.")
            return JsonResponse({'status': 'Ubicación actualizada'})

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Verificar si el usuario es admin
def es_admin(user):
    return user.is_superuser

@login_required
def dispositivos_admin_view(request):
    dispositivos_conectados = Camion.objects.filter(ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5))
    return render(request, 'dispositivos_admin.html', {'dispositivos': dispositivos_conectados})


# Vista para los choferes, donde solo ven su dispositivo
@login_required
def dispositivos_chofer_view(request):
    dispositivo = Camion.objects.get(nombre=request.user.username)  # Asume que el nombre del dispositivo es el username del chofer
    return render(request, 'dispositivos_chofer.html', {'dispositivo': dispositivo})

@login_required
def obtener_ubicaciones(request):
    dispositivos_conectados = Camion.objects.filter(ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5))
    data = []
    for dispositivo in dispositivos_conectados:
        data.append({
            'nombre': dispositivo.nombre,
            'latitud': dispositivo.latitud,
            'longitud': dispositivo.longitud,
        })
    return JsonResponse({'dispositivos': data})


