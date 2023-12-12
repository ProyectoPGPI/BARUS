from django import forms
from django.contrib import admin
from .models import Pedido

class PedidoAdminForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'