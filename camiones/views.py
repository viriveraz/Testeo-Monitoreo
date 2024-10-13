import json
import requests
from django.http import JsonResponse
from .models import Camion
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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

# Obtener ruta desde OSRM
def obtener_ruta(request):
    inicio = '-70.6693,-33.4489'  # Plaza de Armas, Santiago
    fin = '-70.6920,-33.4680'     # Estación Central

    # URL de OSRM
    url = f'http://router.project-osrm.org/route/v1/driving/{inicio};{fin}?overview=full&geometries=geojson'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No se pudo obtener la ruta'}, status=500)

def mostrar_mapa(request):
    return render(request, 'mapa.html')

@csrf_exempt
def actualizar_ubicacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitud = data.get('latitud')
            longitud = data.get('longitud')
            
            # Procesar la ubicación (aquí podrías guardarla en la base de datos si es necesario)
            print(f'Nueva ubicación recibida: {latitud}, {longitud}')
            
            return JsonResponse({'status': 'Ubicación actualizada'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def dispositivos_view(request):
    # Filtramos los camiones que tienen coordenadas asignadas
    camiones = Camion.objects.exclude(latitud=None).exclude(longitud=None)
    context = {'camiones': camiones}
    return render(request, 'dispositivos.html', context)
