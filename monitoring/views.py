from calendar import monthrange
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from parameters.models import PosPaper, Tranzactie, Produs
from django.db.models import Sum, Count
from django.utils import timezone
from api.models import KioskOnline
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
    online_threshold = timezone.now() - timedelta(minutes=5)
    # Get machine status from KioskOnline view
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                pm.pos_id,
                pm.name,
                pm.ip_address,
                pm.token,
                ko.cod_serie,
                ko.ultima_conectare,
                CASE 
                    WHEN ko.ultima_conectare > NOW() - INTERVAL 5 MINUTE THEN 1
                    ELSE 0
                END as is_online
            FROM pos_machines pm
            LEFT JOIN kiosk_online ko ON pm.pos_id = ko.pos_id
            ORDER BY pm.pos_id
        """)
        rows = cursor.fetchall()

    print(f"Fetched {len(rows)} machines from database")  # Debug log
    for row in rows:
        pos_id, name, ip_address, token, cod_serie, ultima_conectare, is_online = row
        print(f"POS {pos_id}: is_online={is_online}, last_seen={ultima_conectare}")
    # machines status
    machines = []
    online_count = 0
    offline_count = 0
    for row in rows:
        pos_id, name, ip_address, token, cod_serie, ultima_conectare, is_online = row
        machines.append({
            'pos_id': pos_id,
            'name': name,
            'ip_address': ip_address,
            'token': token,
            'cod_serie': cod_serie,
            'ultima_conectare': ultima_conectare,
            'is_online': bool(is_online)
        })

        if is_online:
            online_count += 1
        else:
            offline_count += 1

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
        
        # Machine status (machines is a list from raw SQL; sort by pos_id)
        'machines': sorted(machines, key=lambda m: m.get('pos_id')),
        'total_machines': len(machines),
        'online_machines': online_count,
        'offline': offline_count,
        
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
    machines = KioskOnline.objects.all().values('pos_id', 'ip_address', 'is_online', 'last_online')
    return JsonResponse(list(machines), safe=False)

def chart_data(request):
    """API endpoint for chart data"""
    
    # Get time period (default: last 30 days)
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get data per POS
    pos_data = Tranzactie.objects.filter(
        data_tranzactie__gte=start_date
    ).values('pos_id').annotate(
        total_tickets=Sum('cantitate'),
        total_revenue=Sum('total'),
        transaction_count=Count('id')
    ).order_by('pos_id')
    
    # Get data over time (for line charts)
    daily_data = Tranzactie.objects.filter(
        data_tranzactie__gte=start_date
    ).extra(
        select={'day': 'DATE(data_tranzactie)'}
    ).values('day').annotate(
        tickets=Sum('cantitate'),
        revenue=Sum('total')
    ).order_by('day')
    
    return JsonResponse({
        'pos_data': list(pos_data),
        'daily_data': list(daily_data),
        'labels': [f"POS {d['pos_id']}" for d in pos_data],
        'tickets': [d['total_tickets'] for d in pos_data],
        'revenue': [float(d['total_revenue']) for d in pos_data],
    })