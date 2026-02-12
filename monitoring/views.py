from django.http import JsonResponse
from django.shortcuts import render
from parameters.models import PosPaper, TicketMachine, Tranzactie, Produs
from django.db.models import Sum, Count
from django.utils import timezone
import json
from datetime import timedelta
from server_automate_main.monitoring.utils import ping_all_machines

def dashboard(request):
    last_24h = timezone.now() - timedelta(hours=24)

    # machines status
    machines = TicketMachine.objects.all()

    context = {
        'machines': machines.order_by('-is_online','pos_id'),
        'total_machines': machines.count(),
        'online_machines': machines.filter(is_online=True).count(),
        'offline': machines.filter(is_online=False).count(),
    }

    # tickets per POS in last 24h
    stats = (
        Tranzactie.objects
        .filter(data_tranzactie__gte=last_24h)
        .values('pos_id')
        .annotate(
            total_bilete=Sum('cantitate'),
            total_suma=Sum('total'),
            tranzactii=Count('id')
        )
        .order_by('pos_id')
    )
    # POS stats
    pos_labels = [s['pos_id'] for s in stats]
    pos_tickets = [s['total_bilete'] for s in stats]

    print("POS Labels:", pos_labels)
    print("POS Tickets:", pos_tickets)

    # top 10 sold
    products = (
        Tranzactie.objects
        .filter(data_tranzactie__gte=last_24h)
        .values('id_produs', total_bilete=Sum('cantitate'))
        .annotate(sold_count=Sum('cantitate'))
        .order_by('-sold_count')
    )

    # map products id to name 
    product_names = {}
    for p in Produs.objects.all():
        product_names[p.pk] = p.denumire

    product_labels = [product_names.get(p['id_produs'], f"Prod {p['id_produs']}") for p in products]
    product_values = [p['sold_count'] for p in products]

    # calculate paper usage by issued tickets
    paper_labels = []
    paper_remaining = []
    paper_colors = []
    paper_alerts = []

    for paper in PosPaper.objects.all():
        total_per_pos = (
            Tranzactie.objects
            .filter(pos_id=paper.pos_id)
            .aggregate(total_tickets=Sum('cantitate'))
        )

        used = (total_per_pos['total_tickets'] or 0) - paper.tickets_at_last_change
        remaining = paper.roll_capacity - used
        remaining_percent = max((remaining / paper.roll_capacity) * 100, 0)

        if remaining_percent < 10:
            level = 'CRITICAL'
            color = 'rgba(255, 99, 132, 0.8)'   # red
        elif remaining_percent < 20:
            level = 'WARNING'
            color = 'rgba(255, 159, 64, 0.8)'   # orange
        else:
            level = 'OK'
            color = 'rgba(75, 192, 192, 0.8)'   # green

        paper_alerts.append({
            'pos_id': paper.pos_id,
            'remaining': remaining_percent,
            'level': level
            })
        paper_labels.append(f"POS {paper.pos_id}")
        paper_remaining.append(max(remaining_percent, 0))
        paper_colors.append(color)
    context = {
        'stats': stats,
        'pos_labels_json': json.dumps(pos_labels),
        'pos_tickets_json': json.dumps(pos_tickets),
        'product_labels_json': json.dumps(product_labels),
        'product_values_json': json.dumps(product_values),
        'paper_labels_json': json.dumps(paper_labels),
        'paper_remaining_json': json.dumps(paper_remaining),
        'paper_colors_json': json.dumps(paper_colors),
    }
    return render(request, 'core/dashboard.html', context)

def ping_now(request):
    """Trigger ping manually"""
    result = ping_all_machines()
    return JsonResponse({'status': 'ok', 'message': result})

def machine_status_api(request):
    """API endpoint pentru status"""
    machines = TicketMachine.objects.all().values('pos_id', 'ip_address', 'is_online', 'last_online')
    return JsonResponse(list(machines), safe=False)