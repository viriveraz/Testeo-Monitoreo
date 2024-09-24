// Inicializar el mapa centrado en Santiago
var map = L.map('map').setView([-33.4489, -70.6693], 13);

// Cargar los tiles de OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Marcador para la ubicación actual del usuario
var userMarker = L.marker([-33.4489, -70.6693]).addTo(map).bindPopup("Ubicación actual");

// Función para obtener la ubicación del usuario y actualizar el marcador
function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(actualizarUbicacion, mostrarError, {
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

    // Enviar la ubicación al servidor si es necesario
    enviarUbicacionAlServidor(lat, lon);
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

// Función para enviar la ubicación al servidor
function enviarUbicacionAlServidor(lat, lon) {
    fetch('/api/actualizar_ubicacion/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Incluir token CSRF para seguridad en Django
        },
        body: JSON.stringify({
            latitud: lat,
            longitud: lon
        })
    })
    .then(response => {
        if (response.ok) {
            console.log("Ubicación enviada al servidor.");
        } else {
            console.error("Error al enviar la ubicación.");
        }
    })
    .catch(error => console.error('Error:', error));
}

// Obtener el token CSRF en Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Iniciar el monitoreo de geolocalización
obtenerUbicacion();
