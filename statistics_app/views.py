from django.shortcuts import render

def statistics(request):
    # Placeholder data for charts
    yearly_sales = [12000, 15000, 18000, 22000, 30000, 35000]
    product_sales = [5000, 7000, 3000, 4000, 6000]

    context = {
        'yearly_sales': yearly_sales,
        'product_sales': product_sales,
    }
    return render(request, 'statistics_app/dashboard.html', context)
