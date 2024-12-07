from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

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
    en_viaje = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.chofer.username} asignado a {self.camion.patente}'
    
class HistorialViaje(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE, related_name="viajes")
    chofer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="viajes")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ruta = models.TextField(null=True, blank=True)  # JSON con la ruta del viaje
    estado = models.CharField(max_length=50, default="En curso")
    latitud_inicial = models.FloatField(null=True, blank=True) 
    longitud_inicial = models.FloatField(null=True, blank=True) 
    latitud_final = models.FloatField(null=True, blank=True)  
    longitud_final = models.FloatField(null=True, blank=True)
    duracion_total = models.DurationField(null=True, blank=True)
    
    @property
    def duracion_formateada(self):
        if self.duracion_total is None or self.duracion_total < timedelta(seconds=0):
            return "00:00:00"
        
        total_seconds = int(self.duracion_total.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def clean(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    def __str__(self):
        return f"Viaje de {self.chofer.username} en {self.camion.nombre}"

