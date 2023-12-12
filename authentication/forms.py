from django import forms
from .models import Reclamacion

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

class ReclamacionForm(forms.ModelForm):
    class Meta:
        model = Reclamacion
        fields = ['titulo', 'descripcion', 'estado']