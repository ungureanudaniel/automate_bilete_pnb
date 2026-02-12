from pythonping import ping
from django.utils import timezone
from parameters.models import TicketMachine
import threading
from concurrent.futures import ThreadPoolExecutor

def check_machine_status(machine):
    """Ping one machine and update status"""
    try:
        # Timeout 2 secunde, 1 pachet
        response = ping(machine.ip_address, count=1, timeout=2, verbose=False)
        
        if response.success():
            machine.is_online = True
            machine.last_online = timezone.now()
            machine.failure_count = 0
        else:
            machine.is_online = False
            machine.last_offline = timezone.now()
            machine.failure_count += 1
    except Exception:
        machine.is_online = False
        machine.last_offline = timezone.now()
        machine.failure_count += 1
    
    machine.save()
    return machine

def ping_all_machines():
    """Ping all machines in parallel"""
    machines = TicketMachine.objects.all()
    
    # Ping in paralel - mai rapid
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(check_machine_status, machines)
    
    return f"Pinged {machines.count()} machines"