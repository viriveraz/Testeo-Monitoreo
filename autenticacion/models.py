from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLES = [
        ('admin', 'Administrador'),
        ('chofer', 'Chofer'),
    ]
    rol = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"
