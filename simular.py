import requests
import time

# URL de la API para actualizar la ubicación del camión
url_actualizar_ubicacion = 'http://127.0.0.1:8000/api/ubicacion/'

# URL de la API de OSRM para obtener la ruta
url_osrm_ruta = 'http://127.0.0.1:8000/api/ruta/'

# Obtener la ruta desde OSRM (que devuelve una lista de coordenadas)
response = requests.get(url_osrm_ruta)

if response.status_code == 200:
    ruta_osrm = response.json()  # Extraer la ruta en formato GeoJSON o lo que devuelva
    coordenadas_ruta = ruta_osrm['routes'][0]['geometry']['coordinates']  # Asegúrate de ajustar según el formato correcto
else:
    print(f"Error al obtener la ruta: {response.status_code}")
    coordenadas_ruta = []

# Iterar sobre las coordenadas de la ruta y simular el movimiento del camión
for posicion in coordenadas_ruta:
    latitud = posicion[1]
    longitud = posicion[0]

    # Enviar solicitud POST para actualizar la ubicación
    response = requests.post(url_actualizar_ubicacion, json={'latitud': latitud, 'longitud': longitud})

    if response.status_code == 200:
        print(f"Actualización enviada: latitud {latitud}, longitud {longitud}")
    else:
        print(f"Error al enviar la ubicación: {response.status_code}")

    # Esperar 2 segundos antes de enviar la siguiente ubicación
    time.sleep(2)
