# api/models.py
from datetime import timedelta
import os
import subprocess
import platform
from django.db import models

class PosMachine(models.Model):
    pos_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    token = models.CharField(max_length=64, unique=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pos_machines'

    def is_online(self):
        try:
            # Different ping command for Windows vs Linux
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', self.ip_address]
            
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False