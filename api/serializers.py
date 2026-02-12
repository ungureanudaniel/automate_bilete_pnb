# api/serializers.py
from rest_framework import serializers
from parameters.models import Tranzactie

class TranzactieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tranzactie
        fields = ['id_produs', 'cantitate', 'total', 'data_tranzactie', 'pos_id', 'nr']
