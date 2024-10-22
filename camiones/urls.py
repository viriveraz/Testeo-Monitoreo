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

    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:id>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:id>/eliminar/', views.usuario_delete, name='usuario_delete'),

    path('camiones/', views.camiones_list, name='camiones_list'),
    path('camiones/nuevo/', views.camion_create, name='camion_create'),
    path('camiones/<int:id>/editar/', views.camion_update, name='camion_update'),
    path('camiones/<int:id>/eliminar/', views.camion_delete, name='camion_delete'),

    path('asignar-conductor/', views.asignar_conductor, name='asignar_conductor'),

    path('seleccionar_camion/', views.seleccionar_camion, name='seleccionar_camion'),
    path('redirigir-seleccion-camion/', views.redirigir_seleccion_camion, name='redirigir_seleccion_camion'),
]
