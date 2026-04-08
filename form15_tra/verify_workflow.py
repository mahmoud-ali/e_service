from __future__ import annotations

"""
Manual workflow verification helper.

Important:
- This module is imported during normal Django test runs for coverage measurement.
- Therefore it must be import-safe (no top-level django.setup(), no DB writes at import time).
"""

from typing import Any
import os

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.urls import reverse

from form15_tra.models import Market, CollectorAssignment, CollectionForm
from form15_tra.views import CollectionCreateView, CollectionActionView


User = get_user_model()


def setup_test_data() -> tuple[Any, Any, Market]:
    # Clean up in correct order
    CollectionForm.objects.all().delete()
    CollectorAssignment.objects.all().delete()
    User.objects.all().delete()
    Market.objects.all().delete()

    # Create Market
    market = Market.objects.create(market_name="Test Market", location="Test Lacation")

    # Create Observer
    observer_user = User.objects.create_user(username='observer', password='password')
    CollectorAssignment.objects.create(user=observer_user, market=market, is_observer=True)

    # Create Collector
    collector_user = User.objects.create_user(username='collector', password='password')
    a = CollectorAssignment(
        user=collector_user,
        market=market,
        is_collector=True,
        esali_username="esali_u",
        esali_service_id="S1",
    )
    a.set_esali_password_plain("esali_p")
    a.save()

    return observer_user, collector_user, market


def test_workflow() -> None:
    observer, collector, market = setup_test_data()
    factory = RequestFactory()

    print("--- Testing Observer Flow ---")
    
    # 1. Observer creates Draft
    request = factory.post(reverse('collection-create'), data={
        'miner_name': 'Miner A',
        'phone': '0123456789',
        'sacks_count': 10,
    })
    request.user = observer
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionCreateView.as_view()
    response = view(request)
    
    assert response.status_code == 302
    invoice = CollectionForm.objects.last()
    print(f"Observer created invoice: {invoice.status}")
    assert invoice.status == CollectionForm.Status.DRAFT
    assert invoice.collector == observer

    # 2. Observer Confirms Draft -> Collector Confirmation
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice.pk, 'action': 'confirm'}))
    request.user = observer
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice.pk, action='confirm')

    invoice.refresh_from_db()
    print(f"Observer confirmed invoice: {invoice.status}")
    assert invoice.status == CollectionForm.Status.COLLECTOR_CONFIRMATION

    print("--- Testing Collector Approval ---")

    # 3. Collector Confirms Collector Confirmation -> Invoice Requested
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice.pk, 'action': 'approve'}))
    request.user = collector
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice.pk, action='approve')
    
    invoice.refresh_from_db()
    print(f"Collector approved invoice: {invoice.status}")
    assert invoice.status == CollectionForm.Status.INVOICE_REQUESTED

    print("--- Testing Collector Direct Flow ---")
    
    # 4. Collector Creates Draft
    request = factory.post(reverse('collection-create'), data={
        'miner_name': 'Miner B',
        'phone': '0123456789',
        'sacks_count': 5,
    })
    request.user = collector
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionCreateView.as_view()
    response = view(request)
    
    invoice_b = CollectionForm.objects.filter(miner_name='Miner B').last()
    print(f"Collector created invoice: {invoice_b.status}")
    assert invoice_b.status == CollectionForm.Status.DRAFT

    # 5. Collector Confirms -> Invoice Requested
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice_b.pk, 'action': 'confirm'}))
    request.user = collector
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice_b.pk, action='confirm')

    invoice_b.refresh_from_db()
    print(f"Collector confirmed invoice: {invoice_b.status}")
    assert invoice_b.status == CollectionForm.Status.INVOICE_REQUESTED

    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    # When running this file directly, ensure a Django settings module is configured.
    # The main project settings module is `e_service.settings`.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_service.settings")
    test_workflow()
