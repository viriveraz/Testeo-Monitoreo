from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Chofer(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)  # RUT de cada chofer
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rut}"

class Camion(models.Model):
    nombre = models.CharField(max_length=100)
    patente = models.CharField(max_length=20, null=True, blank=True)
    marca = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)
    año = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    latitud = models.FloatField(null=True)
    longitud = models.FloatField(null=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    choferes_asignados = models.ManyToManyField(User, through='AsignacionChofer')

    def __str__(self):
        return self.nombre

    def esta_conectado(self):
        return timezone.now() - self.ultima_actualizacion <= timezone.timedelta(minutes=5)

class AsignacionChofer(models.Model):
    chofer = models.ForeignKey(User, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.chofer.username} asignado a {self.camion.patente}'
