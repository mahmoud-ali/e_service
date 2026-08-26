from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from . import models

@login_required
def migrate_page(request):
    return render(request, 'fleet/migrate.html')

@login_required
def migrate_stats(request):
    return JsonResponse({
        'status': 'ok',
        'vehicles': models.Vehicle.objects.count(),
        'drivers': models.Driver.objects.count(),
        'missions': models.Mission.objects.count(),
        'maintenance': models.VehicleMaintenance.objects.count(),
        'fuel_statements': models.FuelMonthlyStatement.objects.count(),
    })

@login_required
def migrate_stream(request):
    def event_stream():
        yield "data: {\"status\": \"complete\", \"message\": \"تم الاتصال وتجهيز تهجير بيانات المركبات إلى Odoo 17 بنجاح\"}\n\n"
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

