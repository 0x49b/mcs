from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rcon import Client
from django.conf import settings
from rcon import rcon
from django.contrib import messages
from mctools import QUERYClient


# Create your views here.
def index(request):
    query = QUERYClient(host='127.0.0.1', port=25580)
    stats = query.get_full_stats()

    return render(request, 'core/test.html', {'stats': stats})


async def say_hello(request):
    r = ""
    if request.method == 'POST':

        r = await rcon('clear', request.POST.get("playername", ""),
                       host='127.0.0.1',
                       port=settings.RCON_PORT,
                       passwd=settings.RCON_PASSWORD)

    else:

        r = await rcon('say', 'hello',
                       host='127.0.0.1',
                       port=settings.RCON_PORT,
                       passwd=settings.RCON_PASSWORD)

    messages.add_message(request, messages.INFO, r)

    return redirect("index")


async def ban_player(request):
    r = ""
    if request.method == 'POST':
        r = await rcon('ban', request.POST.get("playername", ""), request.POST.get("reason", ""),
                       host='127.0.0.1',
                       port=settings.RCON_PORT,
                       passwd=settings.RCON_PASSWORD)

    messages.add_message(request, messages.INFO, r)

    return redirect("index")


@login_required
def profile_page(request):
    return render(request, 'core/profile.html')
