from django.db import models

from django.db import models

class TicketMachine(models.Model):
    pos_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    last_online = models.DateTimeField(null=True, blank=True)
    last_offline = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    failure_count = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'ticket_machines'
        verbose_name = 'Ticket Machine'
        verbose_name_plural = 'Ticket Machines'
    
    def __str__(self):
        return f"POS {self.pos_id} - {self.ip_address} - {'ONLINE' if self.is_online else 'OFFLINE'}"


class Produs(models.Model):
    denumire = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    valabilitate_zile = models.IntegerField(default=90)

    class Meta:
        managed = False
        db_table = 'produse'
        verbose_name = 'Produs'
        verbose_name_plural = 'Produse'

class Serie(models.Model):
    locatie_pos = models.CharField(max_length=100, default='Locatie')
    serie = models.CharField(max_length=50, default='PNBO')
    numar = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'serii'
        verbose_name = 'Serie'
        verbose_name_plural = 'Serii'

class Tranzactie(models.Model):
    id_produs = models.IntegerField()
    cantitate = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    data_tranzactie = models.DateTimeField()
    pos_id = models.IntegerField()
    nr = models.BigIntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'tranzactii'
        verbose_name = 'Tranzactie'
        verbose_name_plural = 'Tranzactii'

class UserLegacy(models.Model):
    nume = models.CharField(max_length=100)
    parola = models.CharField(max_length=32)
    tip = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'useri'
        verbose_name = 'User Legacy'
        verbose_name_plural = 'Useri Legacy'

class PosPaper(models.Model):
    pos_id = models.IntegerField(primary_key=True)
    tickets_at_last_change = models.IntegerField()
    roll_capacity = models.IntegerField(default=1000)
    last_change = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pos_paper'
