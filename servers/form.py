from django import forms
from .models import ServerProperties


class ServerForm(forms.ModelForm):
    class Meta:
        model = ServerProperties
        fields = "__all__"
