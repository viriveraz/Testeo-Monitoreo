from django.db import models
from django.utils import timezone

class Camion(models.Model):
    nombre = models.CharField(max_length=100)
    latitud = models.FloatField(null=True)  # Cambiado para permitir valores nulos
    longitud = models.FloatField(null=True)  # Cambiado para permitir valores nulos
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def esta_conectado(self):
        # Considera al dispositivo conectado si ha actualizado en los últimos 5 minutos
        return timezone.now() - self.ultima_actualizacion <= timezone.timedelta(minutes=5)
