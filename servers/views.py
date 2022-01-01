import io
import logging
import os.path
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil as psutil
import yaml
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from .models import ServerProperties, ServerBin, Server
from .form import ServerForm, ServerPropertiesForm, UploadFileForm
import requests
from channels.layers import get_channel_layer
from io import StringIO
import shutil
import zipfile


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


def edit_server(request, server_identifier):
    server = Server.objects.get(identifier=server_identifier)
    server_form = ServerForm(instance=server)
    server_properties_form = ServerPropertiesForm(instance=server.server_properties)
    upload_world_form = UploadFileForm()
    bungee_config = None

    if server.server_binary.type == 0:
        confpath = os.path.join(settings.SERVERS_DIR, server_identifier, 'config.yml')
        with open(confpath) as file:
            try:
                bungee_config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)

    return render(request, "servers/edit.html",
                  {'server_form': server_form, 'server_properties_form': server_properties_form,
                   'upload_world_form': upload_world_form, 'server': server, 'bungee_config': bungee_config})


def delete_server(request, server_identifier):
    server = Server.objects.get(identifier=server_identifier)
    stop_single_server(server_identifier)
    path = os.path.join(settings.SERVERS_DIR, server_identifier)
    try:
        shutil.rmtree(path)
        messages.info(request, 'Server %s deleted' % server_identifier)
        server.delete()
    except Exception as e:
        messages.error(request, 'Error deleting erver %s: %s' % (server_identifier, e))

    return redirect('server-overview')


def upload_world(request, server_identifier):
    server = Server.objects.get(identifier=server_identifier)

    if server.server_pid is not None:
        stop_single_server(server_identifier)
        time.sleep(10)

    path = os.path.join(settings.SERVERS_DIR, server_identifier, 'world')

    if request.method == 'POST':
        f = request.FILES['world_file']

        dest = os.path.join(settings.TMP_DIR, f.name)
        with open(dest, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(e)

        try:
            with zipfile.ZipFile(dest, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(settings.SERVERS_DIR, server_identifier))

            with zipfile.ZipFile(dest, 'r') as f:
                names = [info.filename for info in f.infolist() if info.is_dir()]
            world_name = names[0].replace("/", "")
            server_path = os.path.join(settings.SERVERS_DIR, server_identifier)
            os.rename(os.path.join(server_path, world_name), os.path.join(server_path, 'world'))
            os.remove(dest)
        except Exception as e:
            print(e)

        messages.info(request, 'Added new World, you can now start the server again')
    else:
        messages.info(request, 'That didn\'t work')
    return redirect('server-edit', server_identifier)


def remove_world(request, server_identifier):
    path = os.path.join(settings.SERVERS_DIR, server_identifier, 'world')

    stop_single_server(server_identifier)

    try:
        shutil.rmtree(path)
        messages.info(request, 'World %s removed' % server_identifier)
    except Exception as e:
        messages.error(request, 'Error removing world %s: %s' % (server_identifier, e))

    return redirect('server-edit', server_identifier)


def show_server_console(request, server_identifier):
    return render(request, 'servers/console.html', {'server_identifier': server_identifier})


def start_server(request, server_identifier=None):
    if server_identifier is not None:
        if server_identifier == 'all':
            start_all_server()
            messages.info(request, 'Started all servers')
        else:
            start_single_server(server_identifier)
            messages.info(request, 'Server %s started' % server_identifier)

    return redirect('server-overview')


def start_single_server(server_identifier):
    server = Server.objects.get(identifier=server_identifier)
    if check_binary(server.server_binary):
        print(check_server_dir(server))
        if not check_server_dir(server):
            create_server_dir_and_copy_binary(server)
        else:
            start_server_in_thread(server)


def start_all_server():
    print("in all servers")
    servers = Server.objects.all()
    for server in servers:
        start_single_server(server.identifier)


def stop_single_server(server_identifier):
    server = Server.objects.get(identifier=server_identifier)
    try:
        os.kill(int(server.server_pid), signal.SIGTERM)
    except Exception as e:
        print(e)
    server.server_pid = None
    server.save()


def stop_server(request, server_identifier):
    if server_identifier is not None:
        if server_identifier == 'all':
            servers = Server.objects.all()
            for server in servers:
                stop_single_server(server.identifier)
        else:
            stop_single_server(server_identifier)

    messages.info(request, 'Stopped Server')

    return redirect('server-overview')


def restart_server(request, server_identifier):
    if server_identifier is not None:
        if server_identifier == 'all':
            servers = Server.objects.all()
            for server in servers:
                stop_single_server(server.identifier)
                time.sleep(10)
                start_single_server(server.identifier)
        else:
            stop_single_server(server_identifier)
            time.sleep(10)
            start_single_server(server_identifier)

    messages.info(request, 'Restarted Server')
    return redirect('server-overview')


def start_server_in_thread(server):
    x = threading.Thread(target=start_server_thread, args=[server])
    x.start()


def start_server_thread(server):
    servercwd = os.path.join(settings.SERVERS_DIR, server.identifier)
    jarpath = os.path.join(servercwd, server.server_binary.binary_name)

    if server.server_binary.type == 3:
        gui = 'nogui'
    else:
        gui = '--nogui'

    # proc = subprocess.Popen(['python', script], shell=True, #stdout=subprocess.PIPE))

    serverprocess = subprocess.Popen(['java', '-jar', jarpath, gui], cwd=servercwd)
    server.server_pid = serverprocess.pid
    server.save()


def copy_server_binary_to_server_dir(server):
    source = os.path.join(settings.BINARY_DIR, server.server_binary.binary_name)
    destination = os.path.join(settings.SERVERS_DIR, server.identifier)
    shutil.copy(source, destination)


def create_server_dir_and_copy_binary(server):
    path = os.path.join(settings.SERVERS_DIR, server.identifier)
    os.mkdir(path)
    copy_server_binary_to_server_dir(server)
    eula_file = open(os.path.join(settings.SERVERS_DIR, server.identifier, 'eula.txt'), 'a')
    eula_file.write('eula=true')
    eula_file.close()


def check_server_dir(server):
    return os.path.exists(os.path.join(settings.SERVERS_DIR, server.identifier))


def check_binary(binary):
    return os.path.exists(os.path.join(settings.BINARY_DIR, binary.binary_name))


def download_binary(request):
    url = "https://papermc.io/api/v2/projects/paper/versions/1.18.1/builds/103/downloads/paper-1.18.1-103.jar"
    name = url.rsplit('/', 1)[-1]
    server_jar = requests.get(url)
    open(os.path.join(settings.BINARY_DIR, name), 'wb').write(server_jar.content)

    return redirect('server-overview')
