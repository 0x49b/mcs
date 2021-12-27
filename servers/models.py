from datetime import datetime
import random

import requests
import uuid as uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from core.choices import DIFFICULTY, GAMEMODES, SERVER_TYPE
import os


class ServerBin(models.Model):
    class Meta:
        verbose_name = 'Server Binary'
        verbose_name_plural = 'Server Binaries'

    name = models.CharField(max_length=500, blank=False, null=False)
    type = models.IntegerField(choices=SERVER_TYPE, default=0)
    version = models.CharField(max_length=10, blank=False, null=False)
    download_path = models.URLField(blank=False, null=False)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()

        url = self.download_path
        name = url.rsplit('/', 1)[-1]

        if not os.path.exists(os.path.join(settings.BINARY_DIR, name)):
            server_jar = requests.get(url)
            open(os.path.join(settings.BINARY_DIR, name), 'wb').write(server_jar.content)

    def delete(self, using=None, keep_parents=False):
        url = self.download_path
        super().delete()

        name = url.rsplit('/', 1)[-1]
        server_jar = os.path.join(settings.BINARY_DIR, name)
        if os.path.exists(server_jar):
            os.remove(server_jar)


# Create your models here.
class ServerProperties(models.Model):
    class Meta:
        verbose_name = "Server Properties"
        verbose_name_plural = "Servers Properties"

    level_name = models.CharField(max_length=500, blank=False, null=False)
    server_port = models.IntegerField(null=False, blank=False, default=25565)
    query_port = models.IntegerField(null=False, blank=False, default=25580)
    rcon_port = models.IntegerField(null=False, blank=False, default=25570)
    rcon_password = models.CharField(max_length=200, null=False, blank=False)
    server_ip = models.GenericIPAddressField(null=True, blank=True)
    enable_jmx_monitoring = models.BooleanField(default=False)
    enable_command_block = models.BooleanField(default=False)
    gamemode = models.CharField(max_length=10, choices=GAMEMODES, default='survival')
    enable_query = models.BooleanField(default=True)
    motd = models.CharField(max_length=500, blank=False, null=False, default="A Minecraft Server")
    pvp = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=8, choices=DIFFICULTY, default="easy")
    network_compression_threshold = models.IntegerField(default=256, null=False, blank=False)
    max_tick_time = models.IntegerField(default=60000, null=False, blank=False)
    require_resource_pack = models.BooleanField(default=False)
    use_native_transport = models.BooleanField(default=True)
    max_players = models.IntegerField(default=20, null=False, blank=False)
    enable_status = models.BooleanField(default=True)
    online_mode = models.BooleanField(default=True)
    allow_flight = models.BooleanField(default=False)
    broadcast_rcon_to_ops = models.BooleanField(default=True)
    view_distance = models.IntegerField(default=10, null=False, blank=False)
    resource_pack_prompt = models.CharField(max_length=500, null=True, blank=True)
    allow_nether = models.BooleanField(default=True)
    enable_rcon = models.BooleanField(default=True)
    sync_chunk_writes = models.BooleanField(default=True)
    op_permission_level = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(4)],
                                              null=False, blank=False)
    prevent_proxy_connections = models.BooleanField(default=False)
    hide_online_players = models.BooleanField(default=False)
    resource_pack = models.CharField(max_length=500, null=True, blank=True)
    entity_broadcast_range_percentage = models.IntegerField(default=100,
                                                            validators=[MinValueValidator(10), MaxValueValidator(1000)],
                                                            null=False, blank=False)
    simulation_distance = models.IntegerField(default=10, null=False, blank=False)
    player_idle_timeout = models.IntegerField(default=0, null=False, blank=False)
    debug = models.BooleanField(default=False)
    force_gamemode = models.BooleanField(default=False)
    rate_limit = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)], null=False,
                                     blank=False)
    hardcore = models.BooleanField(default=False)
    white_list = models.BooleanField(default=False)
    broadcast_console_to_ops = models.BooleanField(default=True)
    spawn_npcs = models.BooleanField(default=True)
    spawn_animals = models.BooleanField(default=True)
    function_permission_level = models.IntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(4)],
                                                    null=False, blank=False)
    text_filtering_config = models.CharField(max_length=500, null=True, blank=True)
    spawn_monsters = models.BooleanField(default=True)
    enforce_whitelist = models.BooleanField(default=False)
    resource_pack_sha1 = models.CharField(max_length=500, null=True, blank=True)
    spawn_protection = models.IntegerField(default=16, validators=[MinValueValidator(1), MaxValueValidator(1000)],
                                           null=False, blank=False)
    max_world_size = models.IntegerField(default=29999984,
                                         validators=[MinValueValidator(1), MaxValueValidator(29999984)], null=False,
                                         blank=False)

    def __str__(self):
        return self.level_name


class Server(models.Model):
    class Meta:
        verbose_name = "Server"
        verbose_name_plural = "Servers"

    name = models.CharField(max_length=150, null=False, blank=False)
    server_properties = models.OneToOneField(ServerProperties, on_delete=models.CASCADE)
    server_binary = models.OneToOneField(ServerBin, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=10, editable=False)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.identifier is None or self.identifier == "":
            self.identifier = self.create_identifier()
        super().save()

    def create_identifier(self):
        random_string = ''
        for _ in range(10):
            # Considering only upper and lowercase letters
            random_integer = random.randint(97, 97 + 26 - 1)
            flip_bit = random.randint(0, 1)
            # Convert to lowercase if the flip bit is on
            random_integer = random_integer - 32 if flip_bit == 1 else random_integer
            # Keep appending random characters using chr(x)
            random_string += (chr(random_integer))
        return random_string
