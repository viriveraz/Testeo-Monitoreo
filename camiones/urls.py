from .import views
from django.urls import path
from .views import mostrar_mapa, obtener_ubicacion, obtener_ruta,actualizar_ubicacion

urlpatterns = [
    path('api/ubicacion/', actualizar_ubicacion, name='actualizar_ubicacion'),
    path('api/ubicacion/<int:camion_id>/', obtener_ubicacion, name='obtener_ubicacion'),
    path('api/ruta/', obtener_ruta, name='obtener_ruta'),
    path('', mostrar_mapa, name='mostrar_mapa'),
]
