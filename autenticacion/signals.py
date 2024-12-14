# signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from camiones.models import AsignacionChofer, Camion
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfilusuario.save()

# # Asignación automática de camión al inicio de sesión
# @receiver(user_logged_in)
# def asignacion_automatica_al_login(sender, user, request, **kwargs):
#     if user.is_authenticated:
#         # Verificar si el usuario ya tiene una asignación activa
#         asignacion = AsignacionChofer.objects.filter(chofer=user, fecha_fin__isnull=True).first()
#         if not asignacion:
#             # Buscar el primer camión disponible sin asignación
#             camion_disponible = Camion.objects.filter(choferes_asignados__isnull=True).first()
#             if camion_disponible:
#                 # Crear una nueva asignación para el camión disponible
#                 AsignacionChofer.objects.create(chofer=user, camion=camion_disponible)
#                 print("Camión asignado automáticamente al chofer.")
#             else:
#                 print("No hay camiones disponibles para asignar.")

