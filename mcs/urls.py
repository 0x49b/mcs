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
    path('new-server/', serverview.new_server, name='new-server'),
    path('server/binaries/', serverview.binaries_overview, name="server-binaries-overview"),
    path('server/binaries/download', serverview.download_binary, name="server-binaries-download"),


    path('start-server/', dashboardviews.start_server, name="dashboard-start-server"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', coreviews.profile_page, name="profile"),
]
