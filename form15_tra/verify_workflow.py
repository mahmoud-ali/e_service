import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from form15_tra.models import Market, CollectorAssignment, CollectionForm
from django.test import RequestFactory
from django.urls import reverse
from form15_tra.views import CollectionCreateView, CollectionActionView
from django.contrib.messages.storage.fallback import FallbackStorage

def setup_test_data():
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
    CollectorAssignment.objects.create(user=collector_user, market=market, is_collector=True)

    return observer_user, collector_user, market

def test_workflow():
    observer, collector, market = setup_test_data()
    factory = RequestFactory()

    print("--- Testing Observer Flow ---")
    
    # 1. Observer creates Draft
    request = factory.post(reverse('collection-create'), data={
        'miner_name': 'Miner A',
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

    # 2. Observer Confirms Draft -> Waiting Approval
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice.pk, 'action': 'confirm'}))
    request.user = observer
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice.pk, action='confirm')

    invoice.refresh_from_db()
    print(f"Observer confirmed invoice: {invoice.status}")
    assert invoice.status == CollectionForm.Status.WAITING_APPROVAL

    print("--- Testing Collector Approval ---")

    # 3. Collector Approves Waiting Approval -> Pending Payment
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice.pk, 'action': 'approve'}))
    request.user = collector
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice.pk, action='approve')
    
    invoice.refresh_from_db()
    print(f"Collector approved invoice: {invoice.status}")
    assert invoice.status == CollectionForm.Status.PENDING_PAYMENT

    print("--- Testing Collector Direct Flow ---")
    
    # 4. Collector Creates Draft
    request = factory.post(reverse('collection-create'), data={
        'miner_name': 'Miner B',
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

    # 5. Collector Confirms -> Pending Payment
    request = factory.post(reverse('collection-action', kwargs={'pk': invoice_b.pk, 'action': 'confirm'}))
    request.user = collector
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    view = CollectionActionView.as_view()
    response = view(request, pk=invoice_b.pk, action='confirm')

    invoice_b.refresh_from_db()
    print(f"Collector confirmed invoice: {invoice_b.status}")
    assert invoice_b.status == CollectionForm.Status.PENDING_PAYMENT

    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    test_workflow()
