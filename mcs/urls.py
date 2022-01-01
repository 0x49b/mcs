from django.contrib import admin
from django.urls import path, include

from core import views as coreviews
from servers import views as serverview
from dashboard import views as dashboardviews

urlpatterns = [
    path('', dashboardviews.index, name="index"),

    path('admin/', admin.site.urls),

    path('test/', coreviews.index, name='test'),
    path('hello/', coreviews.say_hello, name="hello"),
    path('ban/', coreviews.ban_player, name="ban"),

    path('servers/', serverview.index, name='server-overview'),
    path('server/edit/<str:server_identifier>', serverview.edit_server, name='server-edit'),
    path('server/remove-world/<str:server_identifier>', serverview.remove_world, name='server-remove-world'),
    path('server/upload-world/<str:server_identifier>', serverview.upload_world, name='server-upload-world'),
    path('server/delete/<str:server_identifier>', serverview.delete_server, name='server-delete'),
    path('server/console/<str:server_identifier>', serverview.show_server_console, name='server-console'),
    path('new-server/', serverview.new_server, name='new-server'),
    path('server/binaries/', serverview.binaries_overview, name="server-binaries-overview"),
    path('server/binaries/download', serverview.download_binary, name="server-binaries-download"),
    path('server/start/<str:server_identifier>', serverview.start_server, name="server-start-server"),
    path('server/stop/<str:server_identifier>', serverview.stop_server, name="server-stop-server"),
    path('server/restart/<str:server_identifier>', serverview.restart_server, name="server-restart-server"),

    path('start-server/', dashboardviews.start_server, name="dashboard-start-server"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', coreviews.profile_page, name="profile"),

    path('prometheus/', include('django_prometheus.urls')),
]


