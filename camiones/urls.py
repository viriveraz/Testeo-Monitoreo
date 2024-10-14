from .import views
from django.urls import path
from .views import mostrar_mapa, obtener_ubicacion,actualizar_ubicacion,dispositivos_admin_view, dispositivos_chofer_view

urlpatterns = [
    path('api/ubicacion/', actualizar_ubicacion, name='actualizar_ubicacion'),
    path('api/ubicacion/<int:camion_id>/', obtener_ubicacion, name='obtener_ubicacion'),
    path('', mostrar_mapa, name='mostrar_mapa'),
    path('api/actualizar_ubicacion/', actualizar_ubicacion, name='actualizar_ubicacion'),  # Recibe actualizaciones de ubicación
    path('actualizar-ubicacion/', actualizar_ubicacion, name='actualizar_ubicacion'),
    path('chofer/', views.dispositivos_chofer_view, name='dispositivos_chofer'),
    path('admin/', views.dispositivos_admin_view, name='dispositivos_admin'),
    path('obtener_ubicaciones/', views.obtener_ubicaciones, name='obtener_ubicaciones'),  # Para admin
]
