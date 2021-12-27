import os.path

from django.shortcuts import render, redirect
from django.conf import settings
from .models import ServerProperties, ServerBin, Server
from .form import ServerForm
import requests


# Create your views here.
def index(request):
    servers = Server.objects.all()
    return render(request, 'servers/index.html', {'servers': servers})


def binaries_overview(request):
    binaries = ServerBin.objects.all()
    return render(request, 'servers/binaries-overview.html', {'binaries': binaries})


def new_server(request):
    stu = ServerForm()
    return render(request, "servers/new-server.html", {'form': stu})


def download_binary(request):
    url = "https://papermc.io/api/v2/projects/paper/versions/1.18.1/builds/103/downloads/paper-1.18.1-103.jar"
    name = url.rsplit('/', 1)[-1]
    server_jar = requests.get(url)
    open(os.path.join(settings.BINARY_DIR, name), 'wb').write(server_jar.content)

    return redirect('server-overview')
