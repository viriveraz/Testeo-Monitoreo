from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('camiones/', include('camiones.urls')),
    path('autenticacion/', include('autenticacion.urls')),  # Incluyendo la app de autenticación
    path('', lambda request: redirect('autenticacion/login/')),  # Redirigir la raíz a la página de inicio de sesión
]
