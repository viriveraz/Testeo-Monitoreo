from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('camiones.urls')),  # Incluir las rutas de la app 'camiones'
    path('', lambda request: redirect('mapa/')),  # Redirigir la raíz a /mapa/
]
