from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

class Chofer(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)  # RUT de cada chofer
    fecha_registro = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)  # Número de teléfono en formato internacional
    api_key = models.CharField(max_length=20, null=True, blank=True)  # API Key de CallMeBot

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
    estado = models.CharField(
        max_length=20,
        choices=[('Disponible', 'Disponible'), ('Asignado', 'Asignado')],
        default='Disponible'
    )
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
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Nueva asignación
            if self.camion.estado != 'Disponible':
                raise ValidationError("El camión no está disponible para asignación.")
            self.camion.estado = 'Asignado'
        super().save(*args, **kwargs)
        
        if not self.pk:
            self.camion.save()

    def finalizar(self):
        self.fecha_fin = timezone.now()
        self.camion.estado = 'Disponible'
        self.camion.save()
        self.save()

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
    
class MensajePredefinido(models.Model):
    titulo = models.CharField(max_length=100)
    cuerpo = models.TextField()

    def __str__(self):
        return self.titulo
    

from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Viaje(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_viaje = models.DateTimeField(default=timezone.now)
    origen = models.CharField(max_length=255)
    patente = models.CharField(max_length=20)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    transporte = models.CharField(max_length=255)
    producto = models.CharField(max_length=255)
    fecha_llegada = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='viajes/', null=True, blank=True)
    latitud_inicial = models.FloatField(null=True, blank=True)
    longitud_inicial = models.FloatField(null=True, blank=True)
    latitud_final = models.FloatField(null=True, blank=True)
    longitud_final = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Viaje {self.id} - {self.patente} ({self.estado})"

    def clean(self):
        if self.fecha_llegada and self.fecha_llegada < self.fecha_viaje:
            raise ValidationError("La fecha de llegada no puede ser anterior a la fecha de viaje.")

        if self.latitud_inicial and not -90 <= self.latitud_inicial <= 90:
            raise ValidationError("La latitud inicial debe estar entre -90 y 90.")

        if self.longitud_inicial and not -180 <= self.longitud_inicial <= 180:
            raise ValidationError("La longitud inicial debe estar entre -180 y 180.")

        if self.latitud_final and not -90 <= self.latitud_final <= 90:
            raise ValidationError("La latitud final debe estar entre -90 y 90.")

        if self.longitud_final and not -180 <= self.longitud_final <= 180:
            raise ValidationError("La longitud final debe estar entre -180 y 180.")
