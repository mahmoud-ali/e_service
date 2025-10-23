from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import date, timedelta

from . import models


@login_required
def portal_home(request):
    """Portal home page with dashboard overview"""
    context = {
        'total_vehicles': models.Vehicle.objects.count(),
        'total_drivers': models.Driver.objects.count(),
        'active_missions': models.Mission.objects.filter(
            actual_end_date__isnull=True
        ).count(),
        'upcoming_maintenance': models.VehicleMaintenance.objects.filter(
            next_service_due__gte=date.today(),
            next_service_due__lte=date.today() + timedelta(days=30)
        ).count(),
    }
    return render(request, 'fleet/portal/home.html', context)


@login_required
def vehicle_list(request):
    """List all vehicles"""
    vehicles = models.Vehicle.objects.select_related(
        'model__make', 'fuel_type', 'status'
    ).all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        vehicles = vehicles.filter(status__id=status_filter)
    
    search = request.GET.get('search')
    if search:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=search) |
            Q(model__name__icontains=search) |
            Q(model__make__name__icontains=search)
        )
    
    context = {
        'vehicles': vehicles,
        'statuses': models.VehicleStatus.objects.all(),
        'search': search or '',
        'status_filter': status_filter or '',
    }
    return render(request, 'fleet/portal/vehicle_list.html', context)


@login_required
def vehicle_detail(request, pk):
    """Vehicle detail page"""
    vehicle = get_object_or_404(
        models.Vehicle.objects.select_related('model__make', 'fuel_type', 'status'),
        pk=pk
    )
    
    certificates = models.VehicleCertificate.objects.filter(
        vehicle=vehicle
    ).select_related('cert_type')
    
    assignments = models.VehicleAssignment.objects.filter(
        vehicle=vehicle
    ).order_by('-start_date')
    
    drivers = models.VehicleDriver.objects.filter(
        vehicle=vehicle
    ).select_related('driver').order_by('-start_date')
    
    maintenance_records = models.VehicleMaintenance.objects.filter(
        vehicle=vehicle
    ).select_related('service_type', 'service_provider').order_by('-service_date')
    
    try:
        gps_device = models.VehicleGPSDevice.objects.get(vehicle=vehicle)
    except models.VehicleGPSDevice.DoesNotExist:
        gps_device = None
    
    context = {
        'vehicle': vehicle,
        'certificates': certificates,
        'assignments': assignments,
        'drivers': drivers,
        'maintenance_records': maintenance_records,
        'gps_device': gps_device,
    }
    return render(request, 'fleet/portal/vehicle_detail.html', context)


@login_required
def driver_list(request):
    """List all drivers"""
    drivers = models.Driver.objects.select_related('license_type').all()
    
    search = request.GET.get('search')
    if search:
        drivers = drivers.filter(
            Q(name__icontains=search) |
            Q(license_no__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'drivers': drivers,
        'search': search or '',
    }
    return render(request, 'fleet/portal/driver_list.html', context)


@login_required
def driver_detail(request, pk):
    """Driver detail page"""
    driver = get_object_or_404(
        models.Driver.objects.select_related('license_type'),
        pk=pk
    )
    
    vehicle_assignments = models.VehicleDriver.objects.filter(
        driver=driver
    ).select_related('vehicle__model__make').order_by('-start_date')
    
    missions = models.Mission.objects.filter(
        driver=driver
    ).select_related('vehicle').order_by('-planned_start_date')
    
    context = {
        'driver': driver,
        'vehicle_assignments': vehicle_assignments,
        'missions': missions,
    }
    return render(request, 'fleet/portal/driver_detail.html', context)


@login_required
def mission_list(request):
    """List all missions"""
    missions = models.Mission.objects.select_related(
        'vehicle__model__make', 'driver'
    ).all().order_by('-planned_start_date')
    
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        missions = missions.filter(actual_end_date__isnull=True)
    elif status_filter == 'completed':
        missions = missions.filter(actual_end_date__isnull=False)
    
    search = request.GET.get('search')
    if search:
        missions = missions.filter(
            Q(destination__icontains=search) |
            Q(requested_by__icontains=search) |
            Q(vehicle__license_plate__icontains=search) |
            Q(driver__name__icontains=search)
        )
    
    context = {
        'missions': missions,
        'search': search or '',
        'status_filter': status_filter or '',
    }
    return render(request, 'fleet/portal/mission_list.html', context)


@login_required
def mission_detail(request, pk):
    """Mission detail page"""
    mission = get_object_or_404(
        models.Mission.objects.select_related('vehicle__model__make', 'driver'),
        pk=pk
    )
    
    context = {
        'mission': mission,
    }
    return render(request, 'fleet/portal/mission_detail.html', context)


@login_required
def maintenance_list(request):
    """List all maintenance records"""
    maintenance_records = models.VehicleMaintenance.objects.select_related(
        'vehicle__model__make', 'service_type', 'service_provider'
    ).all().order_by('-service_date')
    
    filter_type = request.GET.get('filter')
    if filter_type == 'upcoming':
        maintenance_records = maintenance_records.filter(
            next_service_due__gte=date.today()
        )
    elif filter_type == 'overdue':
        maintenance_records = maintenance_records.filter(
            next_service_due__lt=date.today(),
            next_service_due__isnull=False
        )
    
    search = request.GET.get('search')
    if search:
        maintenance_records = maintenance_records.filter(
            Q(vehicle__license_plate__icontains=search) |
            Q(service_type__name__icontains=search) |
            Q(service_provider__name__icontains=search)
        )
    
    context = {
        'maintenance_records': maintenance_records,
        'search': search or '',
        'filter_type': filter_type or '',
    }
    return render(request, 'fleet/portal/maintenance_list.html', context)


@login_required
def maintenance_detail(request, pk):
    """Maintenance detail page"""
    maintenance = get_object_or_404(
        models.VehicleMaintenance.objects.select_related(
            'vehicle__model__make', 'service_type', 'service_provider'
        ),
        pk=pk
    )
    
    parts = models.VehicleMaintenancePart.objects.filter(
        maintenance=maintenance
    )
    
    context = {
        'maintenance': maintenance,
        'parts': parts,
    }
    return render(request, 'fleet/portal/maintenance_detail.html', context)
