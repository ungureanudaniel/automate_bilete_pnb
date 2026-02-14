from calendar import monthrange
from django.http import JsonResponse
from django.shortcuts import render
from parameters.models import PosPaper, TicketMachine, Tranzactie, Produs
from django.db.models import Sum, Count
from django.utils import timezone
import json
from datetime import datetime, timedelta
from monitoring.utils import ping_all_machines

def dashboard(request):
    # Current date/time
    now = timezone.now()
    current_year = now.year
    current_month = now.month
    current_month_name = now.strftime('%B')  # e.g., "February"
    # Current year filter
    year_start = timezone.make_aware(datetime(current_year, 1, 1))
    year_end = timezone.make_aware(datetime(current_year, 12, 31, 23, 59, 59))
    
    # Current month filter
    month_start = timezone.make_aware(datetime(current_year, current_month, 1))
    last_day = monthrange(current_year, current_month)[1]
    month_end = timezone.make_aware(datetime(current_year, current_month, last_day, 23, 59, 59))
    
    # Last 30 days, 12 months, 24 hours filters
    last_30d = timezone.now() - timedelta(days=30)
    last_12m = timezone.now() - timedelta(days=365)
    last_24h = timezone.now() - timedelta(hours=24)
    # machines status
    machines = TicketMachine.objects.all()

    # ========== CURRENT YEAR STATS ==========
    year_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[year_start, year_end]
    ).aggregate(
        total_bilete_year=Sum('cantitate'),
        total_suma_year=Sum('total'),
        total_tranzactii_year=Count('id')
    )
    
    # Tickets per POS in current year
    year_pos_stats = (
        Tranzactie.objects
        .filter(data_tranzactie__range=[year_start, year_end])
        .values('pos_id')
        .annotate(
            total_bilete=Sum('cantitate'),
            total_suma=Sum('total'),
            tranzactii=Count('id')
        )
        .order_by('pos_id')
    )
    
    # Top products in current year
    year_products = (
        Tranzactie.objects
        .filter(data_tranzactie__range=[year_start, year_end])
        .values('id_produs')
        .annotate(sold_count=Sum('cantitate'))
        .order_by('-sold_count')
    )
    
    # ========== CURRENT MONTH STATS ==========
    month_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[month_start, month_end]
    ).aggregate(
        total_bilete_month=Sum('cantitate'),
        total_suma_month=Sum('total'),
        total_tranzactii_month=Count('id')
    )
    
    # Tickets per POS in current month
    month_pos_stats = (
        Tranzactie.objects
        .filter(data_tranzactie__range=[month_start, month_end])
        .values('pos_id')
        .annotate(
            total_bilete=Sum('cantitate'),
            total_suma=Sum('total'),
            tranzactii=Count('id')
        )
        .order_by('pos_id')
    )
    
    # Top products in current month
    month_products = (
        Tranzactie.objects
        .filter(data_tranzactie__range=[month_start, month_end])
        .values('id_produs')
        .annotate(sold_count=Sum('cantitate'))
        .order_by('-sold_count')
    )
    
    # ========== MACHINE STATUS (unchanged) ==========
    machines = TicketMachine.objects.all()
    
    # ========== PAPER USAGE (unchanged) ==========
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
            color = 'rgba(255, 99, 132, 0.8)'
        elif remaining_percent < 20:
            level = 'WARNING'
            color = 'rgba(255, 159, 64, 0.8)'
        else:
            level = 'OK'
            color = 'rgba(75, 192, 192, 0.8)'
        
        paper_alerts.append({
            'pos_id': paper.pos_id,
            'remaining': remaining_percent,
            'level': level
        })
        paper_labels.append(f"POS {paper.pos_id}")
        paper_remaining.append(max(remaining_percent, 0))
        paper_colors.append(color)
    
    # ========== PRODUCT NAMES MAPPING ==========
    product_names = {}
    for p in Produs.objects.all():
        product_names[p.pk] = p.denumire
    
    # Prepare chart data for year products
    year_product_labels = [product_names.get(p['id_produs'], f"Prod {p['id_produs']}") for p in year_products]
    year_product_values = [p['sold_count'] for p in year_products]
    
    # Prepare chart data for month products
    month_product_labels = [product_names.get(p['id_produs'], f"Prod {p['id_produs']}") for p in month_products]
    month_product_values = [p['sold_count'] for p in month_products]
    
    # Prepare POS chart data
    year_pos_labels = [s['pos_id'] for s in year_pos_stats]
    year_pos_tickets = [s['total_bilete'] for s in year_pos_stats]
    
    month_pos_labels = [s['pos_id'] for s in month_pos_stats]
    month_pos_tickets = [s['total_bilete'] for s in month_pos_stats]
    
    context = {
        # Yearly data
        'year': current_year,
        'year_stats': year_stats,
        'year_pos_labels_json': json.dumps(year_pos_labels),
        'year_pos_tickets_json': json.dumps(year_pos_tickets),
        'year_product_labels_json': json.dumps(year_product_labels),
        'year_product_values_json': json.dumps(year_product_values),
        
        # Monthly data
        'month': current_month_name,
        'month_stats': month_stats,
        'month_pos_labels_json': json.dumps(month_pos_labels),
        'month_pos_tickets_json': json.dumps(month_pos_tickets),
        'month_product_labels_json': json.dumps(month_product_labels),
        'month_product_values_json': json.dumps(month_product_values),
        
        # Machine status
        'machines': machines.order_by('-is_online', 'pos_id'),
        'total_machines': machines.count(),
        'online_machines': machines.filter(is_online=True).count(),
        'offline': machines.filter(is_online=False).count(),
        
        # Paper data
        'paper_labels_json': json.dumps(paper_labels),
        'paper_remaining_json': json.dumps(paper_remaining),
        'paper_colors_json': json.dumps(paper_colors),
        'paper_alerts': paper_alerts,
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