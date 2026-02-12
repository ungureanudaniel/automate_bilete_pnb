from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

def health_check(request):
    return HttpResponse('Health OK', content_type='text/plain')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/', include('api.urls')),
    path('', include('monitoring.urls')),
    path('parameters/', include('parameters.urls')),
]
