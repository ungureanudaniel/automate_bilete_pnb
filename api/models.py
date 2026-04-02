# api/models.py
from datetime import timedelta, timezone
import os
import subprocess
import platform
from django.db import models
from django.utils import timezone as django_timezone

class PosMachine(models.Model):
    pos_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    token = models.CharField(max_length=64, unique=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pos_machines'

    @property
    def is_online(self):
        """Return True if heartbeat received in last 5 minutes"""
        if not self.last_seen:
            return False
        return django_timezone.now() - self.last_seen < timedelta(minutes=5)
        
    def update_last_seen(self):
        """Update last_seen timestamp"""
        self.last_seen = django_timezone.now()
        self.save(update_fields=['last_seen'])
        
    def __str__(self):
        status = "🟢" if self.is_online else "🔴"
        return f"{status} {self.name} (POS {self.pos_id}) - {self.ip_address}"