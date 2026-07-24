from datetime import datetime, timedelta
from django.utils import timezone
from parameters.models import Tranzactie
from django.shortcuts import render
from calendar import monthrange
from django.http import JsonResponse
from django.db.models import Sum, Count
import json

def sales_details(request):
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

    # ========== TOTAL STATS ==========
    total_stats = Tranzactie.objects.aggregate(
        total_bilete=Sum('cantitate'),
        total_suma=Sum('total'),
        total_tranzactii=Count('id')
    )
    # ========== CURRENT YEAR STATS ==========
    year_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[year_start, year_end]
    ).aggregate(
        total_bilete_year=Sum('cantitate'),
        total_suma_year=Sum('total'),
        total_tranzactii_year=Count('id')
    )
    year_pos_tickets = Tranzactie.objects.filter(
        data_tranzactie__range=[year_start, year_end]
    ).values('pos_id').annotate(total_bilete=Sum('cantitate')).order_by('pos_id')
    year_product_values = Tranzactie.objects.filter(
        data_tranzactie__range=[year_start, year_end]
    ).values('id_produs').annotate(total_suma=Sum('total')).order_by('-total_suma')
    # ========== CURRENT MONTH STATS ==========
    month_stats = Tranzactie.objects.filter(
        data_tranzactie__range=[month_start, month_end]
    ).aggregate(
        total_bilete_month=Sum('cantitate'),
        total_suma_month=Sum('total'),
        total_tranzactii_month=Count('id')
    )
    month_pos_tickets = Tranzactie.objects.filter(
        data_tranzactie__range=[month_start, month_end]
    ).values('pos_id').annotate(total_bilete=Sum('cantitate')).order_by('pos_id')
    month_product_values = Tranzactie.objects.filter(
        data_tranzactie__range=[month_start, month_end]
    ).values('id_produs').annotate(total_suma=Sum('total')).order_by('-total_suma')

    context = {
        # total data
        'total_stats': total_stats,

        # Yearly data
        'year': current_year,
        'year_stats': year_stats,
        'year_pos_tickets_json': json.dumps(year_pos_tickets),
        'year_product_values_json': json.dumps(year_product_values),

        # Monthly data
        'month': current_month_name,
        'month_stats': month_stats,
        'month_pos_tickets_json': json.dumps(month_pos_tickets),
        'month_product_values_json': json.dumps(month_product_values),
    }

    return render(request, 'sales_details.html', context)
