# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from parameters.models import Tranzactie
from .models import PosMachine
from .serializers import TranzactieSerializer
from django.utils import timezone

# Simple token auth
def check_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        machine = PosMachine.objects.get(token=token)
        machine.last_seen = timezone.now()
        machine.save(update_fields=['last_seen'])
        return machine
    except PosMachine.DoesNotExist:
        return None

@api_view(['POST'])
def create_ticket(request):
    machine = check_token(request)
    if not machine:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = TranzactieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'ticket_id': serializer.data.get('nr', None), 'status': 'ok'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def heartbeat(request):
    machine = check_token(request)
    if not machine:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'status': 'alive', 'last_seen': machine.last_seen})
