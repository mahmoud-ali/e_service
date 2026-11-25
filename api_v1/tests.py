from datetime import date
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import Http404
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from . import views
from .serializers import (
    GoldProductionMasterSerializer,
    GoldShippingMasterSerializer,
    GoldTravelMasterSerializer,
)


class FakeDoesNotExist(Exception):
    pass


class FakeModel:
    DoesNotExist = FakeDoesNotExist


class FakeDetailItem:
    def __init__(self, id):
        self.id = id


class FakeItem:
    def __init__(self, id, state, d, details=None):
        self.id = id
        self.state = state
        self.date = d
        # Simulate reverse relation manager by being iterable
        self.appmovegolddetails_set = details or []


class FakeQuerySet:
    """
    Minimal QuerySet-like object supporting filter(), get(), iteration,
    and a .model with DoesNotExist for get_object_or_404 compatibility.
    """
    model = FakeModel

    def __init__(self, items):
        self._items = list(items)

    def filter(self, **kwargs):
        def matches(obj):
            for k, v in kwargs.items():
                if getattr(obj, k) != v:
                    return False
            return True

        return FakeQuerySet([obj for obj in self._items if matches(obj)])

    def get(self, **kwargs):
        filtered = self.filter(**kwargs)._items
        if len(filtered) != 1:
            raise FakeDoesNotExist()
        return filtered[0]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class DummyListSerializer:
    def __init__(self, instance=None, many=False):
        if many:
            self.data = [{'id': obj.id} for obj in instance]
        else:
            self.data = {'id': instance.id}


class DummyDetailSerializer:
    def __init__(self, instance=None, many=False):
        if many:
            # Represent detail items minimally
            self.data = [{'id': getattr(obj, 'id', None)} for obj in instance]
        else:
            self.data = {'id': getattr(instance, 'id', None)}


class DummyMasterSerializer:
    def __init__(self, instance=None, many=False):
        # Only the fields we assert on in tests
        self.data = {
            'id': getattr(instance, 'id', None),
            'alloy_list': getattr(instance, 'alloy_list', None),
        }


class GoldTravelViewsTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="user1", password="pass")
        self.user_no_group = self.User.objects.create_user(username="user2", password="pass")
        self.group = Group.objects.create(name='baldna_gold_travel')
        self.user.groups.add(self.group)

    def test_list_requires_authentication(self):
        view = views.GoldTravelListView.as_view()
        request = self.factory.get('/gold_travel_list/2025-10-01/')
        response = view(request, date='2025-10-01')
        self.assertEqual(response.status_code, 401)

    def test_list_requires_group(self):
        view = views.GoldTravelListView.as_view()
        request = self.factory.get('/gold_travel_list/2025-10-01/')
        force_authenticate(request, user=self.user_no_group)
        response = view(request, date='2025-10-01')
        self.assertEqual(response.status_code, 403)

    def test_list_returns_filtered_ids(self):
        # Patch the view to use dummy queryset and serializer, and stub AppMoveGold constants
        items = [
            FakeItem(1, state='SMRC', d=date(2025, 10, 1)),
            FakeItem(2, state='OTHER', d=date(2025, 10, 1)),
            FakeItem(3, state='SMRC', d=date(2025, 10, 2)),
            FakeItem(4, state='SMRC', d=date(2025, 10, 1)),
        ]
        queryset = FakeQuerySet(items)

        # Authenticate a user in the required group
        request = self.factory.get('/gold_travel_list/2025-10-01/')
        force_authenticate(request, user=self.user)

        # Apply patches
        original_queryset = views.GoldTravelListView.queryset
        original_serializer = views.GoldTravelListView.serializer_class
        original_model = views.AppMoveGold
        try:
            views.GoldTravelListView.queryset = queryset
            views.GoldTravelListView.serializer_class = DummyListSerializer

            # Stub AppMoveGold so the view's reference to STATE_SMRC resolves
            class _StubModel:
                STATE_SMRC = 'SMRC'
            views.AppMoveGold = _StubModel

            view = views.GoldTravelListView.as_view()
            response = view(request, date='2025-10-01')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {'app_list': [1, 4]})
        finally:
            views.GoldTravelListView.queryset = original_queryset
            views.GoldTravelListView.serializer_class = original_serializer
            views.AppMoveGold = original_model

    def test_list_invalid_date_message(self):
        # Authenticate a user in the required group
        request = self.factory.get('/gold_travel_list/not-a-date/')
        force_authenticate(request, user=self.user)

        view = views.GoldTravelListView.as_view()
        response = view(request, date='not-a-date')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Invalid date format. Use YYYY-MM-DD.")

    def test_detail_requires_authentication(self):
        view = views.GoldTravelDetailView.as_view()
        request = self.factory.get('/gold_travel_retrieve/1/')
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_detail_requires_group(self):
        view = views.GoldTravelDetailView.as_view()
        request = self.factory.get('/gold_travel_retrieve/1/')
        force_authenticate(request, user=self.user_no_group)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 403)

    def test_detail_not_found(self):
        # Empty queryset so .get() raises DoesNotExist -> Http404 -> NotFound
        queryset = FakeQuerySet([])

        # Authenticate a user in the required group
        request = self.factory.get('/gold_travel_retrieve/999/')
        force_authenticate(request, user=self.user)

        # Patch serializer and queryset
        original_queryset = views.GoldTravelDetailView.queryset
        original_master_serializer = views.GoldTravelDetailView.serializer_class
        try:
            views.GoldTravelDetailView.queryset = queryset
            views.GoldTravelDetailView.serializer_class = DummyMasterSerializer

            view = views.GoldTravelDetailView.as_view()
            response = view(request, pk=999)

            self.assertEqual(response.status_code, 404)
            self.assertIn("No request found with request_number: 999.", str(response.data.get('detail')))
        finally:
            views.GoldTravelDetailView.queryset = original_queryset
            views.GoldTravelDetailView.serializer_class = original_master_serializer

    def test_detail_success(self):
        # Build a fake object with details
        details = [FakeDetailItem(10), FakeDetailItem(20)]
        obj = FakeItem(1, state='SMRC', d=date(2025, 10, 1), details=details)
        queryset = FakeQuerySet([obj])

        # Authenticate a user in the required group
        request = self.factory.get('/gold_travel_retrieve/1/')
        force_authenticate(request, user=self.user)

        # Patch serializers and queryset
        original_queryset = views.GoldTravelDetailView.queryset
        original_master_serializer = views.GoldTravelDetailView.serializer_class
        original_detail_serializer = views.GoldTravelDetailSerializer
        try:
            views.GoldTravelDetailView.queryset = queryset
            views.GoldTravelDetailView.serializer_class = DummyMasterSerializer
            views.GoldTravelDetailSerializer = DummyDetailSerializer

            view = views.GoldTravelDetailView.as_view()
            response = view(request, pk=1)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['id'], 1)
            self.assertEqual(response.data['alloy_list'], [{'id': 10}, {'id': 20}])
        finally:
            views.GoldTravelDetailView.queryset = original_queryset
            views.GoldTravelDetailView.serializer_class = original_master_serializer
            views.GoldTravelDetailSerializer = original_detail_serializer


class CompanyRegistrationFieldsSerializerTests(TestCase):
    """Flat company registration fields on the master serializers."""

    def _company(self, **overrides):
        values = {
            'name': 'شركة الاختبار',
            'name_ar': 'شركة الاختبار',
            'commercial_register_no': 'CR-123',
            'tax_number': 'TAX-456',
            'zakat_file_no': 'ZK-789',
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def _travel(self, company):
        return SimpleNamespace(
            id=1,
            code='RN/1',
            date=date(2025, 10, 1),
            destination=1,
            get_destination_display=lambda: 'SSMO',
            owner_name_lst=company,
            owner_address='بورتسودان',
            repr_name='repr',
            repr_address='addr',
            repr_phone='0123',
            repr_identity_type=1,
            get_repr_identity_type_display=lambda: 'passport',
            repr_identity='555',
            repr_identity_issue_date=date(2020, 1, 30),
            alloy_list=[],
        )

    def _production(self, company):
        return SimpleNamespace(
            id=1,
            form_no='P/1',
            date=date(2025, 10, 1),
            license=SimpleNamespace(company=company),
            state=1,
            get_state_display=lambda: 'draft',
            alloy_jaf=0,
            alloy_khabath=0,
            alloy_remaind=0,
            alloy_weight_expected=0,
            goldproductionformalloy_set=[],
        )

    def _shipping(self, company):
        return SimpleNamespace(
            id=1,
            form_no='S/1',
            date=date(2025, 10, 1),
            license=SimpleNamespace(company=company),
            state=1,
            get_state_display=lambda: 'draft',
            goldshippingformalloy_set=[],
        )

    def test_travel_master_has_registration_fields(self):
        data = GoldTravelMasterSerializer(self._travel(self._company())).data

        self.assertEqual(data['commercial_register_no'], 'CR-123')
        self.assertEqual(data['tax_number'], 'TAX-456')
        self.assertEqual(data['zakat_file_no'], 'ZK-789')
        self.assertEqual(data['company_name'], 'شركة الاختبار')

    def test_production_master_has_registration_fields(self):
        data = GoldProductionMasterSerializer(self._production(self._company())).data

        self.assertEqual(data['commercial_register_no'], 'CR-123')
        self.assertEqual(data['tax_number'], 'TAX-456')
        self.assertEqual(data['zakat_file_no'], 'ZK-789')
        self.assertEqual(data['company'], 'شركة الاختبار')

    def test_shipping_master_has_registration_fields(self):
        data = GoldShippingMasterSerializer(self._shipping(self._company())).data

        self.assertEqual(data['commercial_register_no'], 'CR-123')
        self.assertEqual(data['tax_number'], 'TAX-456')
        self.assertEqual(data['zakat_file_no'], 'ZK-789')
        self.assertEqual(data['company'], 'شركة الاختبار')

    def test_null_registration_fields_serialize_as_null(self):
        company = self._company(
            commercial_register_no=None,
            tax_number=None,
            zakat_file_no=None,
        )

        for data in (
            GoldTravelMasterSerializer(self._travel(company)).data,
            GoldProductionMasterSerializer(self._production(company)).data,
            GoldShippingMasterSerializer(self._shipping(company)).data,
        ):
            self.assertIsNone(data['commercial_register_no'])
            self.assertIsNone(data['tax_number'])
            self.assertIsNone(data['zakat_file_no'])
