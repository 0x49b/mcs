from django.contrib import admin
from servers.models import ServerProperties, ServerBin, Server


# Register your models here.
class ServerPropertiesAdmin(admin.ModelAdmin):
    list_display = (
        'level_name',
        'server_port',
        'query_port',
        'rcon_port',
    )


class ServerBinAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'version')


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_properties', 'server_binary',)


admin.site.register(ServerProperties, ServerPropertiesAdmin)
admin.site.register(ServerBin, ServerBinAdmin)
admin.site.register(Server, ServerAdmin)
