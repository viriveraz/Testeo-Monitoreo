// Función para obtener el token CSRF desde las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verifica si esta cookie empieza con el nombre dado
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Inicializar el mapa centrado en una posición inicial (Santiago)
var map = L.map('map').setView([-33.4489, -70.6693], 13);

// Cargar los tiles de OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Crear un marcador para el dispositivo
var userMarker = L.marker([-33.4489, -70.6693]).addTo(map).bindPopup("Ubicación actual");

function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;

            // Imprimir las coordenadas actuales en la consola
            console.log("Ubicación actual: Latitud = " + lat + ", Longitud = " + lon);

            // Actualizar la posición del marcador
            userMarker.setLatLng([lat, lon]).update();

            // Cambiar la vista del mapa a la nueva posición
            map.setView([lat, lon], 13);

            // Actualizar el popup con la nueva ubicación
            userMarker.bindPopup("Tu ubicación actual: " + lat.toFixed(6) + ", " + lon.toFixed(6)).openPopup();

            // Enviar la ubicación al servidor
            enviarUbicacionAlServidor(lat, lon);

        }, mostrarError);
    } else {
        alert("Geolocalización no disponible en tu navegador.");
    }
}


// Función para enviar la ubicación al servidor
function enviarUbicacionAlServidor(lat, lon) {
    fetch('/camiones/actualizar-ubicacion/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken // Asegúrate de incluir el token CSRF si es necesario
        },
        body: JSON.stringify({
            latitud: lat,
            longitud: lon,
            nombre: dispositivoNombre // Nombre del dispositivo dinámico desde el usuario autenticado
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al enviar la ubicación al servidor');
        }
        return response.json();
    })
    .then(data => {
        console.log("Ubicación enviada correctamente al servidor.");
    })
    .catch(error => console.error("Error al enviar la ubicación:", error));
}


// Manejo de errores en geolocalización
function mostrarError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("Permiso de geolocalización denegado.");
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

// Llamar a la función obtenerUbicacion cada 5 segundos para actualizar la ubicación
setInterval(obtenerUbicacion, 5000);

// Llamar a la función obtenerUbicacion cuando se cargue la página
obtenerUbicacion();
