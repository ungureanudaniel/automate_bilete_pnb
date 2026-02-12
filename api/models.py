# api/models.py
from django.db import models

class PosMachine(models.Model):
    pos_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=64, unique=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pos_machines'
