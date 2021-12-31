from django import forms
from .models import Server, ServerProperties
from .validators import validate_file


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = (
            'name',
            'server_properties',
            'server_binary',
        )


class ServerPropertiesForm(forms.ModelForm):
    class Meta:
        model = ServerProperties
        fields = "__all__"


class UploadFileForm(forms.Form):
    world_file = forms.FileField()
