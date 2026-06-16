from django.shortcuts import render

def sales_details(request):
    # Placeholder data - replace with actual database queries
    sales_data = {
        'total_sales': 150000,
        'total_orders': 1200,
        'average_order_value': 125,
        'top_products': [
            {'name': 'Product A', 'sales': 50000},
            {'name': 'Product B', 'sales': 30000},
            {'name': 'Product C', 'sales': 20000},
        ],
    }
    
    return render(request, '/sales_details.html', {'sales_data': sales_data})
