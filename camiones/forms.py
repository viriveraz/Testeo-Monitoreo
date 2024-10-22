from django import forms
from django.contrib.auth.models import User
from .models import Camion, AsignacionChofer

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['nombre', 'patente', 'marca', 'modelo', 'año', 'color']

class AsignacionChoferForm(forms.ModelForm):
    class Meta:
        model = AsignacionChofer
        fields = ['chofer', 'camion', 'fecha_inicio', 'fecha_fin']
