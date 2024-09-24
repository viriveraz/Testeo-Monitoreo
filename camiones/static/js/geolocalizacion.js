// Inicializar el mapa centrado en Santiago
var map = L.map('map').setView([-33.4489, -70.6693], 13);

// Cargar los tiles de OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Marcador para la ubicación actual del usuario
var userMarker = L.marker([-33.4489, -70.6693]).addTo(map).bindPopup("Ubicación actual");

// Diccionario de destinos con sus coordenadas
var destinos = {
    "Plaza de Armas": [-33.4372, -70.6506],
    "Estación Central": [-33.4513, -70.6803]
};

// Función para obtener la ubicación del usuario y actualizar el marcador
function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(actualizarUbicacion, mostrarError, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        });
    } else {
        alert("La geolocalización no está disponible en este navegador.");
    }
}

// Función para actualizar la ubicación
function actualizarUbicacion(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;

    // Actualizar el marcador en el mapa
    userMarker.setLatLng([lat, lon]).update();
    map.setView([lat, lon], 13);

    userMarker.bindPopup("Tu ubicación: " + lat + ", " + lon).openPopup();
}

// Función para generar la ruta utilizando OSRM
function generarRuta(latOrigen, lonOrigen, latDestino, lonDestino) {
    var osrmUrl = `https://router.project-osrm.org/route/v1/driving/${lonOrigen},${latOrigen};${lonDestino},${latDestino}?geometries=geojson&overview=full`;

    fetch(osrmUrl)
    .then(response => response.json())
    .then(data => {
        if (data.routes && data.routes.length > 0) {
            var route = data.routes[0].geometry;

            // Dibujar la ruta en el mapa
            L.geoJSON(route, {
                style: {
                    color: 'blue',
                    weight: 5
                }
            }).addTo(map);
            console.log("Ruta generada correctamente");
        } else {
            alert("No se pudo encontrar una ruta.");
        }
    })
    .catch(error => console.error('Error al obtener la ruta:', error));
}

// Manejo de errores
function mostrarError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("Permiso denegado.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Ubicación no disponible.");
            break;
        case error.TIMEOUT:
            alert("Tiempo de espera agotado.");
            break;
        case error.UNKNOWN_ERROR:
            alert("Error desconocido.");
            break;
    }
}

// Añadir el evento al botón para generar la ruta
document.addEventListener("DOMContentLoaded", function() {
    var generarRutaBtn = document.getElementById("generarRutaBtn");
    var destinoSelect = document.getElementById("destinoSelect");

    if (generarRutaBtn && destinoSelect) {
        generarRutaBtn.addEventListener("click", function() {
            var destinoSeleccionado = destinoSelect.value;
            var destinoCoords = destinos[destinoSeleccionado];

            if (destinoCoords) {
                // Obtener la ubicación actual del usuario
                navigator.geolocation.getCurrentPosition(function(position) {
                    var latActual = position.coords.latitude;
                    var lonActual = position.coords.longitude;

                    console.log("Ubicación actual: " + latActual + ", " + lonActual);
                    console.log("Destino seleccionado: " + destinoCoords[0] + ", " + destinoCoords[1]);

                    // Generar la ruta desde la ubicación actual hasta el destino seleccionado
                    generarRuta(latActual, lonActual, destinoCoords[0], destinoCoords[1]);
                }, mostrarError);
            }
        });
    }
});

// Iniciar el monitoreo de geolocalización
obtenerUbicacion();
