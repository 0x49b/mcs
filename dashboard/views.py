import os.path
import subprocess
import threading
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect


@login_required
def index(request):
    return render(request, 'dashboard/index.html')


@login_required
def start_server(request):
    x = threading.Thread(target=start_server_thread)
    x.start()
    return redirect("index")


def start_server_thread():
    servercwd = os.path.join(settings.MEDIA_ROOT, "papermc")
    jarpath = os.path.join(servercwd, "paper-1.18.1-101.jar")

    serverprocess = subprocess.Popen(['java', '-jar', jarpath, 'nogui'], cwd=servercwd)
    print(serverprocess.pid)
