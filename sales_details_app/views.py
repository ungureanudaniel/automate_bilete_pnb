from datetime import datetime, timedelta
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from parameters.models import Tranzactie
from django.shortcuts import render
from calendar import monthrange
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum, Count
import json

from api.models import PosMachine

def sales_details(request):
    # Current date/time
    now = timezone.now()
    current_year = now.year
    current_month = now.month
    current_month_name = now.strftime('%B')  # e.g., "February"

    period = request.GET.get('period', 'all')
    selected_pos = request.GET.get('pos_id', None)
    page = request.GET.get('page', 1)
    date_filter = {}

    if period == 'today':
        start_date = timezone.make_aware(datetime(now.year, now.month, now.day))
        end_date = start_date + timedelta(days=1)
        date_filter = {'data_tranzactie__gte': start_date, 'data_tranzactie__lt': end_date} 
    elif period == 'week':  
        start_date = timezone.make_aware(datetime(now.year, now.month, now.day)) - timedelta(days=now.weekday())
        end_date = start_date + timedelta(days=7)
        date_filter = {'data_tranzactie__gte': start_date, 'data_tranzactie__lt': end_date}
    elif period == 'month':
        start_date = timezone.make_aware(datetime(now.year, now.month, 1))
        last_day = monthrange(now.year, now.month)[1]
        end_date = timezone.make_aware(datetime(now.year, now.month, last_day, 23, 59, 59))
        date_filter = {'data_tranzactie__gte': start_date, 'data_tranzactie__lt': end_date}
    elif period == 'year':
        start_date = timezone.make_aware(datetime(now.year, 1, 1))
        end_date = timezone.make_aware(datetime(now.year, 12, 31, 23, 59, 59))
        date_filter = {'data_tranzactie__gte': start_date, 'data_tranzactie__lt': end_date}
    else:  # Default to all time
        date_filter = {}

    # build the queryset based on filters
    transactions = Tranzactie.objects.all()

    # Apply date filter if it exists
    if date_filter:
        transactions = transactions.filter(**date_filter)
    # Apply POS filter if it exists
    if selected_pos:
        transactions = transactions.filter(pos_id=selected_pos)

    transactions = transactions.order_by('-data_tranzactie')
    
    # ========== TOTAL STATS ==========
    total_stats = Tranzactie.objects.aggregate(
        total_bilete=Sum('cantitate'),
        total_suma=Sum('total'),
        total_tranzactii=Count('id')
    )
    total_tranzactii = total_stats.get('total_tranzactii', 0) or 1
    total_bilete = total_stats.get('total_bilete', 0) or 1
    total_suma = total_stats.get('total_suma', 0) or 0

    avg_transaction_value = total_suma / total_tranzactii if total_tranzactii > 0 else 0
    avg_ticket_value = total_suma / total_bilete if total_bilete > 0 else 0

    # ========== PAGINATION ==========
    paginator = Paginator(transactions, 50)  # 50 transactions per page
    page_obj = paginator.get_page(page)

    year_start = timezone.make_aware(datetime(current_year, 1, 1))
    year_end = timezone.make_aware(datetime(current_year, 12, 31, 23, 59, 59))

    year_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[year_start, year_end]
    ).aggregate(
        total_bilete_year=Sum('cantitate'),
        total_suma_year=Sum('total'),
        total_tranzactii_year=Count('id')
    )

    month_start = timezone.make_aware(datetime(current_year, current_month, 1))
    last_day = monthrange(current_year, current_month)[1]
    month_end = timezone.make_aware(datetime(current_year, current_month, last_day, 23, 59, 59))
    
    month_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[month_start, month_end]
    ).aggregate(
        total_bilete_month=Sum('cantitate'),
        total_suma_month=Sum('total'),
        total_tranzactii_month=Count('id')
    )

    # ========== CONTEXT ==========
    context = {
        # Filter params
        'period': period,
        'selected_pos': int(selected_pos) if selected_pos else '',
        
        # Stats
        'stats': total_stats,
        'year_stats': year_stats,
        'month_stats': month_stats,
        'avg_transaction_value': avg_transaction_value,
        'avg_ticket_value': avg_ticket_value,
        
        # Data
        'transactions': page_obj,
        'machines': PosMachine.objects.all().order_by('pos_id'),
        'product': Tranzactie.objects.values('id_produs').distinct().order_by('id_produs'),
        # Year info
        'year': current_year,
        'month': current_month_name,
    }

    return render(request, 'sales_details.html', context)
