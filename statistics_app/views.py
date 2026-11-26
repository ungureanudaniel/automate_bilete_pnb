from django.utils import timezone
from datetime import datetime, timedelta
from parameters.models import Tranzactie
from django.shortcuts import render
from calendar import monthrange
from django.db.models import Sum, Count
from django.core.paginator import Paginator

def statistics(request):
    """
    View to render the statistics page with monthly, yearly, and all-time sales data.
    """
    now = timezone.now()
    current_year = now.year
    current_month = now.month
    current_month_name = now.strftime('%B')  # e.g., "February"

    curr_year_start = timezone.make_aware(datetime(current_year, 1, 1))
    curr_year_end = timezone.make_aware(datetime(current_year, 12, 31, 23, 59, 59))

    curr_month_start = timezone.make_aware(datetime(current_year, current_month, 1))
    curr_month_last_day = monthrange(current_year, current_month)[1]
    curr_month_end = timezone.make_aware(datetime(current_year, current_month, curr_month_last_day, 23, 59, 59))
    
    # build the queryset based on filters
    transactions = Tranzactie.objects.all()
    
    # Apply date filter if it exists
    curr_year_transactions = transactions.filter(data_tranzactie__range=[curr_year_start, curr_year_end])
    curr_month_transactions = transactions.filter(data_tranzactie__range=[curr_month_start, curr_month_end])
    
        
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

    monthly_sales = [
        {'month': 'January', 'sales': 1000},
        {'month': 'February', 'sales': 1500},
        {'month': 'March', 'sales': 2000},
        # Add more months as needed
    ]
    yearly_sales = [
        {'year': 2021, 'sales': 12000},
        {'year': 2022, 'sales': 15000},
        {'year': 2023, 'sales': 18000},
    ]
    all_time_sales = [
        {'period': 'All Time', 'sales': 50000},
    ]
    context = {
        'total_tickets': total_bilete,
        'total_sales': total_suma,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'all_time_sales': all_time_sales,
    }
    return render(request, 'statistics.html', context)
