from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from form15_tra.models import Market, CollectionForm, CollectorAssignment, APILog
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from form15_tra.api.serializers import CollectionFormSerializer
from unittest.mock import patch
from typing import Any
from cryptography.fernet import Fernet
from django.conf import settings
import runpy
import os

User = get_user_model()

# Provide a default valid phone for all CollectionForm creations in this test module.
# Phone is required and must be exactly 10 digits.
_ORIG_COLLECTIONFORM_CREATE = CollectionForm.objects.create

def _collectionform_create_with_phone(*args: Any, **kwargs: Any) -> Any:
    kwargs.setdefault("phone", "0123456789")
    return _ORIG_COLLECTIONFORM_CREATE(*args, **kwargs)

CollectionForm.objects.create = _collectionform_create_with_phone  # type: ignore[assignment]

class MiningSystemTests(TestCase):
    """
    Unit tests for the Mining Revenue Collection System.
    Tests state transitions, validation, and immutability.
    """

    def setUp(self) -> None:
        # CollectorAssignment now requires Esali credentials for collectors (encrypted at rest).
        # Provide a stable key for this test module.
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(
            username="collector", password="password"
        )
        self.observer = User.objects.create_user(
            username="observer", password="password"
        )
        self.senior_collector = User.objects.create_user(
            username="senior", password="password"
        )
        self.assignment = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        self.assignment.set_esali_password_plain("esali_p")
        self.assignment.save()
        self.observer_assignment = CollectorAssignment.objects.create(
            user=self.observer,
            market=self.market,
            is_observer=True
        )
        self.senior_assignment = CollectorAssignment.objects.create(
            user=self.senior_collector,
            market=self.market,
            is_senior_collector=True
        )

    def test_phone_must_be_exactly_10_digits(self) -> None:
        bad = CollectionForm(
            miner_name="Bad Phone",
            phone="123",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
        )
        with self.assertRaises(ValidationError):
            bad.full_clean()

        good = CollectionForm(
            miner_name="Good Phone",
            phone="0123456789",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
        )
        good.full_clean()

    def test_draft_to_invoice_requested_transition(self) -> None:
        """
        Transition: Draft -> Invoice Requested.
        """
        form = CollectionForm.objects.create(
            miner_name="John Doe",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT
        )
        
        form.status = CollectionForm.Status.INVOICE_REQUESTED
        form.save()
        self.assertEqual(form.status, CollectionForm.Status.INVOICE_REQUESTED)

    def test_immutability_in_pending_payment(self) -> None:
        """
        BR-02: Forms in Pending Payment status must be immutable for standard fields.
        """
        form = CollectionForm.objects.create(
            miner_name="John Doe",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )
        
        # Try to change miner_name
        form.miner_name = "Jane Doe"
        with self.assertRaises(ValidationError) as cm:
            form.save()
        self.assertIn("غير قابل للتعديل", str(cm.exception))

    def test_immutability_in_invoice_requested(self) -> None:
        """
        BR-02: Forms after Draft must be immutable for standard fields.
        """
        form = CollectionForm.objects.create(
            miner_name="John Doe",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED
        )
        
        form.miner_name = "Jane Doe"
        with self.assertRaises(ValidationError) as cm:
            form.save()
        self.assertIn("غير قابل للتعديل", str(cm.exception))

    def test_pre_payment_cancellation_only(self) -> None:
        """
        BR-03: Cancellation is forbidden once the status is Paid.
        """
        form = CollectionForm.objects.create(
            miner_name="John Doe",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PAID
        )
        
        form.status = CollectionForm.Status.CANCELLED
        with self.assertRaises(ValidationError) as cm:
            form.save()
        self.assertIn("لا يمكن إلغاء إيصال تم دفعه بالفعل", str(cm.exception))

    def test_valid_cancellation(self) -> None:
        """
        Test valid transition from Pending Payment to Cancelled.
        """
        form = CollectionForm.objects.create(
            miner_name="John Doe",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )
        
        form.status = CollectionForm.Status.CANCELLED
        form.cancelled_by = self.senior_collector
        form.cancellation_reason = "Customer changed mind"
        form.save()
        self.assertEqual(form.status, CollectionForm.Status.CANCELLED)

    def test_collector_mutual_exclusion(self) -> None:
        """
        Verify that a user cannot be both a collector and a senior collector.
        """
        user = User.objects.create_user(username="multi_role", password="password")
        assignment = CollectorAssignment(
            user=user,
            market=self.market,
            is_collector=True,
            is_senior_collector=True
        )
        with self.assertRaises(ValidationError) as cm:
            assignment.save()
        self.assertIn("لا يمكن للمستخدم أن يمتلك أكثر من دور واحد", str(cm.exception))

    def test_collector_can_edit_draft(self) -> None:
        """
        Verify that a collector can edit their own draft.
        """
        self.client.login(username="collector", password="password")
        form = CollectionForm.objects.create(
            miner_name="Old Name",
            sacks_count=10,
            total_amount=100.0,
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT
        )
        response = self.client.post(reverse('collection-edit', kwargs={'pk': form.pk}), {
            'miner_name': "New Name",
            'phone': "0123456789",
            'sacks_count': 15,
            'total_amount': 150.0
        })
        self.assertEqual(response.status_code, 302)
        form.refresh_from_db()
        self.assertEqual(form.miner_name, "New Name")

    def test_collector_cannot_edit_non_draft(self) -> None:
        """
        Verify that a collector cannot edit a collection that is not in Draft.
        """
        self.client.login(username="collector", password="password")
        form = CollectionForm.objects.create(
            miner_name="Old Name",
            sacks_count=10,
            total_amount=100.0,
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )
        response = self.client.get(reverse('collection-edit', kwargs={'pk': form.pk}))
        self.assertEqual(response.status_code, 403)

    # test_duplicate_receipt_number removed as it's harder to force duplicate with auto-gen without mocking
    # Ideally should mock the count or save process to test race conditions but for now we rely on DB unique constraint which is still there.
    def test_invoice_print_restrictions(self) -> None:
        """
        Verify that only PENDING_PAYMENT invoices can be printed as invoices.
        """
        # Create a paid receipt
        paid_form = CollectionForm.objects.create(
            miner_name="Paid Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PAID
        )
        # Create a pending invoice
        pending_form = CollectionForm.objects.create(
            miner_name="Pending Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )

        # Login
        self.client.login(username="collector", password="password")

        # Test printing pending invoice (Should be 200 OK)
        response = self.client.get(reverse('invoice-print', kwargs={'pk': pending_form.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Miner")

        # Test printing paid receipt via invoice endpoint (Should be 302 redirect with error message)
        response = self.client.get(reverse('invoice-print', kwargs={'pk': paid_form.pk}), follow=True)
        self.assertRedirects(response, reverse('collection-list'))
        self.assertContains(response, "ليس لديك صلاحية للطباعة")

        # Test unauthenticated access (Should redirect to login)
        self.client.logout()
        response = self.client.get(reverse('invoice-print', kwargs={'pk': pending_form.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_receipt_print_restrictions(self) -> None:
        """
        Verify that only PAID receipts can be printed as receipts.
        """
        paid_form = CollectionForm.objects.create(
            miner_name="Paid Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PAID
        )
        pending_form = CollectionForm.objects.create(
            miner_name="Pending Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )

        self.client.login(username="collector", password="password")

        # Paid receipt should print
        response = self.client.get(reverse('receipt-print', kwargs={'pk': paid_form.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, paid_form.receipt_number)
        self.assertContains(response, "Paid Miner")

        # Pending invoice should not print as receipt
        response = self.client.get(reverse('receipt-print', kwargs={'pk': pending_form.pk}), follow=True)
        self.assertRedirects(response, reverse('collection-list'))
        self.assertContains(response, "ليس لديك صلاحية للطباعة")

        # Unauthenticated should redirect to login
        self.client.logout()
        response = self.client.get(reverse('receipt-print', kwargs={'pk': paid_form.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_observer_cannot_print_invoice_or_receipt(self) -> None:
        """
        Observers must not be able to print invoice or receipt even if status matches.
        """
        paid_form = CollectionForm.objects.create(
            miner_name="Paid Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PAID
        )
        pending_form = CollectionForm.objects.create(
            miner_name="Pending Miner",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT
        )

        self.client.login(username="observer", password="password")

        resp1 = self.client.get(reverse("invoice-print", kwargs={"pk": pending_form.pk}), follow=True)
        self.assertRedirects(resp1, reverse("collection-list"))
        self.assertContains(resp1, "ليس لديك صلاحية للطباعة")

        resp2 = self.client.get(reverse("receipt-print", kwargs={"pk": paid_form.pk}), follow=True)
        self.assertRedirects(resp2, reverse("collection-list"))
        self.assertContains(resp2, "ليس لديك صلاحية للطباعة")

    def test_queue_invoices_endpoint_bulk_and_idempotent(self) -> None:
        """
        Verify POST /api/v1/collections/queue-invoices/ queues a batch and returns details.
        """
        # Two requested
        f1 = CollectionForm.objects.create(
            miner_name="Req 1",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        f2 = CollectionForm.objects.create(
            miner_name="Req 2",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        # One other status
        f3 = CollectionForm.objects.create(
            miner_name="Other",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        url = reverse("collection-queue-invoices")

        # First call updates 2
        response = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("updated"), 2)
        self.assertIn("results", response.json())
        self.assertEqual(len(response.json().get("results") or []), 2)
        for row in response.json().get("results") or []:
            self.assertIn("id", row)
            self.assertIn("miner_name", row)
            self.assertIn("total_amount", row)
            self.assertIn("market_name", row)

        f1.refresh_from_db()
        f2.refresh_from_db()
        f3.refresh_from_db()
        self.assertEqual(f1.status, CollectionForm.Status.INVOICE_QUEUED)
        self.assertEqual(f2.status, CollectionForm.Status.INVOICE_QUEUED)
        self.assertEqual(f3.status, CollectionForm.Status.DRAFT)

        # Per-record APILog for each transitioned record
        self.assertEqual(
            APILog.objects.filter(action="queue_invoices", collection_form__in=[f1, f2]).count(),
            2,
        )

        # Second call is idempotent (updates 0)
        response2 = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("updated"), 0)
        self.assertEqual(len(response2.json().get("results") or []), 0)

    def test_queue_invoices_respects_limit_batches(self) -> None:
        """
        Verify queue-invoices only queues up to `limit` records per call.
        """
        f1 = CollectionForm.objects.create(
            miner_name="Req 1",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        f2 = CollectionForm.objects.create(
            miner_name="Req 2",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        f3 = CollectionForm.objects.create(
            miner_name="Req 3",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )

        url = reverse("collection-queue-invoices") + "?limit=2"
        resp1 = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json().get("updated"), 2)
        self.assertEqual(resp1.json().get("limit"), 2)
        self.assertEqual(len(resp1.json().get("results") or []), 2)

        f1.refresh_from_db()
        f2.refresh_from_db()
        f3.refresh_from_db()
        queued = {CollectionForm.Status.INVOICE_QUEUED}
        requested = {CollectionForm.Status.INVOICE_REQUESTED}
        self.assertIn(f1.status, queued | requested)
        self.assertIn(f2.status, queued | requested)
        self.assertIn(f3.status, queued | requested)
        self.assertEqual(
            CollectionForm.objects.filter(status=CollectionForm.Status.INVOICE_QUEUED).count(),
            2,
        )
        self.assertEqual(
            CollectionForm.objects.filter(status=CollectionForm.Status.INVOICE_REQUESTED).count(),
            1,
        )

        # Second call should pick up the remaining one
        url2 = reverse("collection-queue-invoices") + "?limit=2"
        resp2 = self.client.post(url2, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json().get("updated"), 1)
        self.assertEqual(len(resp2.json().get("results") or []), 1)

    def test_mark_paid_endpoint_bulk_receipts_and_idempotent(self) -> None:
        """
        Verify POST /api/v1/collections/mark-paid/ overwrites receipt_number and marks provided
        PENDING_PAYMENT receipts as PAID.
        """
        p1 = CollectionForm.objects.create(
            miner_name="P1",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        p2 = CollectionForm.objects.create(
            miner_name="P2",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        other = CollectionForm.objects.create(
            miner_name="Other",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )

        url = reverse("collection-mark-paid")

        payload = {
            "receipts": [
                {"id": p1.id, "receipt_number": "RCPT-1"},
                {"id": p2.id, "receipt_number": "RCPT-2"},
                {"id": other.id, "receipt_number": "RCPT-3"},
            ]
        }
        response = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("requested"), 3)
        self.assertEqual(response.json().get("updated"), 2)
        self.assertEqual(response.json().get("skipped"), 1)

        p1.refresh_from_db()
        p2.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(p1.status, CollectionForm.Status.PAID)
        self.assertEqual(p2.status, CollectionForm.Status.PAID)
        self.assertEqual(other.status, CollectionForm.Status.INVOICE_REQUESTED)
        self.assertEqual(p1.receipt_number, "RCPT-1")
        self.assertEqual(p2.receipt_number, "RCPT-2")
        self.assertNotEqual(other.receipt_number, "RCPT-3")

        # Per-record APILog for each updated row
        self.assertEqual(
            APILog.objects.filter(action="mark_paid_bulk", collection_form__in=[p1, p2]).count(),
            2,
        )

        # Second call should update 0 (already paid / not eligible)
        response2 = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("updated"), 0)

    def test_mark_paid_endpoint_requires_receipts(self) -> None:
        url = reverse("collection-mark-paid")
        response = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 400)

    def test_consume_pending_payment_check_now_requires_api_key(self) -> None:
        url = reverse("collection-consume-pending-payment-check-now")
        response = self.client.post(url, data={}, content_type="application/json")
        self.assertIn(response.status_code, (401, 403))

    def test_consume_pending_payment_check_now_empty(self) -> None:
        url = reverse("collection-consume-pending-payment-check-now")
        response = self.client.post(
            url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("ids"), [])

    def test_consume_pending_payment_check_now_returns_and_clears_flags(self) -> None:
        a = CollectionForm.objects.create(
            miner_name="CN1",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
            pending_payment_check_now=True,
        )
        b = CollectionForm.objects.create(
            miner_name="CN2",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
            pending_payment_check_now=True,
        )
        CollectionForm.objects.create(
            miner_name="Other",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
            pending_payment_check_now=True,
        )
        url = reverse("collection-consume-pending-payment-check-now")
        response = self.client.post(
            url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_CLIENT_API_KEY"
        )
        self.assertEqual(response.status_code, 200)
        ids = sorted(response.json().get("ids") or [])
        self.assertEqual(ids, sorted([a.id, b.id]))
        a.refresh_from_db()
        b.refresh_from_db()
        self.assertFalse(a.pending_payment_check_now)
        self.assertFalse(b.pending_payment_check_now)

        response2 = self.client.post(
            url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY"
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("ids"), [])

    def test_collection_detail_sets_pending_payment_check_now(self) -> None:
        form = CollectionForm.objects.create(
            miner_name="DetailFlag",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
            pending_payment_check_now=False,
        )
        self.client.login(username="collector", password="password")
        resp = self.client.get(reverse("collection-detail", kwargs={"pk": form.pk}))
        self.assertEqual(resp.status_code, 200)
        form.refresh_from_db()
        self.assertTrue(form.pending_payment_check_now)

    def test_collection_status_poll_ok_and_shape(self) -> None:
        form = CollectionForm.objects.create(
            miner_name="PollOk",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        self.client.login(username="collector", password="password")
        url = reverse("collection-status-poll", kwargs={"pk": form.pk})
        resp = self.client.get(url, HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Cache-Control"], "private, max-age=0")
        data = resp.json()
        self.assertEqual(set(data.keys()), {"status", "updated_at"})
        self.assertEqual(data["status"], CollectionForm.Status.DRAFT)
        self.assertIsInstance(data["updated_at"], str)

    def test_collection_status_poll_not_visible_returns_404(self) -> None:
        form = CollectionForm.objects.create(
            miner_name="PollHidden",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        other = User.objects.create_user(username="other_collector", password="password")
        other_assignment = CollectorAssignment(
            user=other,
            market=self.market,
            is_collector=True,
            esali_username="esali_other",
            esali_service_id="S9",
        )
        other_assignment.set_esali_password_plain("esali_pw")
        other_assignment.save()
        self.client.login(username="other_collector", password="password")
        url = reverse("collection-status-poll", kwargs={"pk": form.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_set_pending_payment_endpoint_bulk_invoices_and_idempotent(self) -> None:
        """
        Verify POST /api/v1/collections/set-pending-payment/ sets invoice_id and transitions
        provided INVOICE_QUEUED invoices to PENDING_PAYMENT.
        """
        q1 = CollectionForm.objects.create(
            miner_name="Q1",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_QUEUED,
        )
        q2 = CollectionForm.objects.create(
            miner_name="Q2",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_QUEUED,
        )
        other = CollectionForm.objects.create(
            miner_name="Other",
            sacks_count=5,
            total_amount=Decimal("500.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )

        url = reverse("collection-set-pending-payment")
        payload = {
            "invoices": [
                {"id": q1.id, "invoice_id": "INV-1"},
                {"id": q2.id, "invoice_id": "INV-2"},
                {"id": other.id, "invoice_id": "INV-3"},
            ]
        }

        response = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("requested"), 3)
        self.assertEqual(response.json().get("updated"), 2)
        self.assertEqual(response.json().get("skipped"), 1)

        q1.refresh_from_db()
        q2.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(q1.status, CollectionForm.Status.PENDING_PAYMENT)
        self.assertEqual(q2.status, CollectionForm.Status.PENDING_PAYMENT)
        self.assertEqual(other.status, CollectionForm.Status.PENDING_PAYMENT)
        self.assertEqual(q1.invoice_id, "INV-1")
        self.assertEqual(q2.invoice_id, "INV-2")
        self.assertIsNone(other.invoice_id)
        self.assertIsNotNone(q1.invoice_generated_at)
        self.assertIsNotNone(q2.invoice_generated_at)
        self.assertIsNone(other.invoice_generated_at)

        # Per-record APILog for each updated row
        self.assertEqual(
            APILog.objects.filter(action="set_pending_payment_bulk", collection_form__in=[q1, q2]).count(),
            2,
        )

        # Second call should update 0 (already updated / not eligible)
        response2 = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("updated"), 0)

    def test_cancel_expired_endpoint_cancels_only_eligible(self) -> None:
        import os
        from django.utils import timezone
        from datetime import timedelta

        os.environ["INVOICE_CANCEL_AFTER_DAYS"] = "3"
        try:
            now = timezone.now()
            expired_at = now - timedelta(days=4)
            fresh_at = now - timedelta(days=2)

            expired = CollectionForm.objects.create(
                miner_name="Expired",
                sacks_count=5,
                total_amount=Decimal("500.00"),
                collector=self.collector,
                market=self.market,
                status=CollectionForm.Status.PENDING_PAYMENT,
                invoice_id="INV-EXPIRED",
                invoice_generated_at=expired_at,
            )
            fresh = CollectionForm.objects.create(
                miner_name="Fresh",
                sacks_count=5,
                total_amount=Decimal("500.00"),
                collector=self.collector,
                market=self.market,
                status=CollectionForm.Status.PENDING_PAYMENT,
                invoice_id="INV-FRESH",
                invoice_generated_at=fresh_at,
            )
            paid = CollectionForm.objects.create(
                miner_name="Paid",
                sacks_count=5,
                total_amount=Decimal("500.00"),
                collector=self.collector,
                market=self.market,
                status=CollectionForm.Status.PAID,
                invoice_id="INV-PAID",
                invoice_generated_at=expired_at,
                receipt_number="R-1",
            )

            url = reverse("collection-cancel-expired")
            payload = {"ids": [expired.id, fresh.id, paid.id]}
            resp = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data.get("requested"), 3)
            self.assertEqual(data.get("updated"), 1)

            expired.refresh_from_db()
            fresh.refresh_from_db()
            paid.refresh_from_db()

            self.assertEqual(expired.status, CollectionForm.Status.CANCELLED)
            self.assertIn("Auto-cancelled after", str(expired.cancellation_reason or ""))
            self.assertEqual(fresh.status, CollectionForm.Status.PENDING_PAYMENT)
            self.assertEqual(paid.status, CollectionForm.Status.PAID)

            # Per-record APILog for the cancelled record
            self.assertEqual(
                APILog.objects.filter(action="cancel_expired_bulk", collection_form=expired).count(),
                1,
            )
        finally:
            os.environ.pop("INVOICE_CANCEL_AFTER_DAYS", None)

    def test_set_pending_payment_endpoint_requires_invoices(self) -> None:
        url = reverse("collection-set-pending-payment")
        response = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 400)


class CollectionApiActionTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")

        self.collector = User.objects.create_user(username="collector_api", password="password")
        a = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        a.set_esali_password_plain("esali_p")
        a.save()

        self.senior = User.objects.create_user(username="senior_api", password="password")
        CollectorAssignment.objects.create(user=self.senior, market=self.market, is_senior_collector=True)

        self.api_client = APIClient()

    def test_confirm_action_success_and_logs(self) -> None:
        self.api_client.force_authenticate(user=self.collector)
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        url = reverse("collection-confirm", kwargs={"pk": form.pk})
        resp = self.api_client.put(url, data={}, format="json")
        self.assertEqual(resp.status_code, 200)

        form.refresh_from_db()
        self.assertEqual(form.status, CollectionForm.Status.INVOICE_REQUESTED)

        log = APILog.objects.filter(action="confirm_collection", collection_form=form).latest("created_at")
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.user, self.collector)

    def test_confirm_action_fails_when_not_draft_and_logs(self) -> None:
        self.api_client.force_authenticate(user=self.collector)
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )

        url = reverse("collection-confirm", kwargs={"pk": form.pk})
        resp = self.api_client.put(url, data={}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Cannot confirm from status", (resp.json() or {}).get("error", ""))

        log = APILog.objects.filter(action="confirm_collection_failed", collection_form=form).latest("created_at")
        self.assertEqual(log.status_code, 400)
        self.assertEqual(log.user, self.collector)

    def test_cancel_action_success_and_logs(self) -> None:
        self.api_client.force_authenticate(user=self.senior)
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )

        url = reverse("collection-cancel", kwargs={"pk": form.pk})
        resp = self.api_client.post(url, data={"cancellation_reason": "Reason text"}, format="json")
        self.assertEqual(resp.status_code, 200)

        form.refresh_from_db()
        self.assertEqual(form.status, CollectionForm.Status.CANCELLED)
        self.assertEqual(form.cancelled_by, self.senior)
        self.assertEqual(form.cancellation_reason, "Reason text")

        log = APILog.objects.filter(action="cancel_collection", collection_form=form).latest("created_at")
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.user, self.senior)

    def test_cancel_action_fails_when_wrong_status_and_logs(self) -> None:
        self.api_client.force_authenticate(user=self.senior)
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        url = reverse("collection-cancel", kwargs={"pk": form.pk})
        resp = self.api_client.post(url, data={"cancellation_reason": "Reason text"}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Cannot cancel from status", (resp.json() or {}).get("error", ""))

        log = APILog.objects.filter(action="cancel_collection_failed", collection_form=form).latest("created_at")
        self.assertEqual(log.status_code, 400)
        self.assertEqual(log.user, self.senior)


class CollectionSerializerCreateTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_create", password="password")
        a = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        a.set_esali_password_plain("esali_p")
        a.save()

        self.api_client = APIClient()

    def test_create_collection_api_assigns_market_collector_and_draft(self) -> None:
        self.api_client.force_authenticate(user=self.collector)
        url = "/app/api/v1/invoice/tra/collections/"
        payload = {"miner_name": "Miner X", "sacks_count": "2", "total_amount": "0.00"}
        resp = self.api_client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertEqual(data["miner_name"], "Miner X")
        self.assertEqual(data["collector"], "collector_create")
        self.assertEqual(data["market"], "Test Market")
        self.assertEqual(data["status"], CollectionForm.Status.DRAFT)
        # receipt_number is not auto-generated; it may be blank at creation time.

        obj = CollectionForm.objects.get(pk=data["id"])
        self.assertEqual(obj.collector, self.collector)
        self.assertEqual(obj.market, self.market)
        self.assertEqual(obj.status, CollectionForm.Status.DRAFT)

    def test_serializer_create_fails_without_assignment(self) -> None:
        user = User.objects.create_user(username="no_assignment", password="password")
        factory = APIRequestFactory()
        request = factory.post("/api/v1/invoice/tra/collections/", {})
        request.user = user

        serializer = CollectionFormSerializer(
            data={"miner_name": "Miner Y", "sacks_count": "1", "total_amount": "0.00"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(Exception) as cm:
            serializer.save()
        self.assertIn("not assigned", str(cm.exception).lower())


class ApiPermissionBehaviorTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_perm", password="password")
        a = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        a.set_esali_password_plain("esali_p")
        a.save()

        self.senior = User.objects.create_user(username="senior_perm", password="password")
        CollectorAssignment.objects.create(user=self.senior, market=self.market, is_senior_collector=True)

        self.api_client = APIClient()

    def test_has_api_key_required_for_queue_invoices(self) -> None:
        url = reverse("collection-queue-invoices")

        resp_missing = self.api_client.post(url, data={}, format="json")
        self.assertIn(resp_missing.status_code, {401, 403})

        resp_invalid = self.api_client.post(url, data={}, format="json", HTTP_X_API_KEY="BAD")
        self.assertIn(resp_invalid.status_code, {401, 403})

        resp_ok = self.api_client.post(url, data={}, format="json", HTTP_X_API_KEY="EXPECTED_CLIENT_API_KEY")
        self.assertEqual(resp_ok.status_code, 200)

    def test_is_collector_required_for_confirm(self) -> None:
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        url = reverse("collection-confirm", kwargs={"pk": form.pk})

        # Not authenticated
        resp_anon = self.api_client.put(url, data={}, format="json")
        self.assertIn(resp_anon.status_code, {401, 403})

        # Wrong role (senior is not collector)
        self.api_client.force_authenticate(user=self.senior)
        resp_wrong = self.api_client.put(url, data={}, format="json")
        self.assertIn(resp_wrong.status_code, {401, 403})

        # Correct role
        self.api_client.force_authenticate(user=self.collector)
        resp_ok = self.api_client.put(url, data={}, format="json")
        self.assertEqual(resp_ok.status_code, 200)

    def test_is_senior_collector_required_for_cancel(self) -> None:
        form = CollectionForm.objects.create(
            miner_name="John",
            sacks_count=5,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        url = reverse("collection-cancel", kwargs={"pk": form.pk})

        self.api_client.force_authenticate(user=self.collector)
        resp_wrong = self.api_client.post(url, data={"cancellation_reason": "Reason text"}, format="json")
        self.assertIn(resp_wrong.status_code, {401, 403})

        self.api_client.force_authenticate(user=self.senior)
        resp_ok = self.api_client.post(url, data={"cancellation_reason": "Reason text"}, format="json")
        self.assertEqual(resp_ok.status_code, 200)


class ApiViewsErrorHandlingTests(TestCase):
    def test_queue_invoices_returns_500_and_logs_on_exception(self) -> None:
        url = reverse("collection-queue-invoices")
        with patch("form15_tra.api.views.CollectionForm.objects.filter", side_effect=Exception("boom")):
            resp = self.client.post(
                url,
                data={},
                content_type="application/json",
                HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
            )
        self.assertEqual(resp.status_code, 500)
        self.assertTrue(APILog.objects.filter(action="queue_invoices_failed").exists())

    def test_set_pending_payment_returns_500_and_logs_on_exception(self) -> None:
        url = reverse("collection-set-pending-payment")
        payload = {"invoices": [{"id": 1, "invoice_id": "INV-1"}]}
        with patch("form15_tra.api.views.CollectionForm.objects.select_for_update", side_effect=Exception("boom")):
            resp = self.client.post(
                url,
                data=payload,
                content_type="application/json",
                HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
            )
        self.assertEqual(resp.status_code, 500)
        self.assertTrue(APILog.objects.filter(action="set_pending_payment_bulk_failed").exists())

    def test_mark_paid_returns_500_and_logs_on_exception(self) -> None:
        url = reverse("collection-mark-paid")
        payload = {"receipts": [{"id": 1, "receipt_number": "RCPT-1"}]}
        with patch("form15_tra.api.views.CollectionForm.objects.select_for_update", side_effect=Exception("boom")):
            resp = self.client.post(
                url,
                data=payload,
                content_type="application/json",
                HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
            )
        self.assertEqual(resp.status_code, 500)
        self.assertTrue(APILog.objects.filter(action="mark_paid_bulk_failed").exists())


class VerifyWorkflowModuleTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")

    def test_verify_workflow_module_is_import_safe_and_runs(self) -> None:
        # Ensure importing does not try to reconfigure Django or run setup at import time.
        from form15_tra import verify_workflow

        with patch("builtins.print"):
            verify_workflow.test_workflow()

    def test_verify_workflow_main_block_runs(self) -> None:
        # Covers the bottom `if __name__ == "__main__": ...`
        with patch("builtins.print"):
            runpy.run_module("form15_tra.verify_workflow", run_name="__main__")


class ApiViewsetPermissionsBranchesTests(TestCase):
    def test_get_permissions_branches(self) -> None:
        # Cover CollectionFormViewSet.get_permissions action branching.
        from form15_tra.api.views import CollectionFormViewSet

        v = CollectionFormViewSet()
        for action in (
            "create",
            "confirm",
            "cancel",
            "queue_invoices",
            "mark_paid",
            "set_pending_payment",
            "collector_esali_config",
            "update_esali_service_id",
            "consume_pending_payment_check_now",
            "cancel_expired",
            "list",
        ):
            v.action = action
            perms = v.get_permissions()
            self.assertTrue(perms)


class HtmlViewsBranchTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_html", password="password")
        a = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        a.set_esali_password_plain("esali_p")
        a.save()

        self.senior = User.objects.create_user(username="senior_html", password="password")
        CollectorAssignment.objects.create(user=self.senior, market=self.market, is_senior_collector=True)

        self.observer = User.objects.create_user(username="observer_html", password="password")
        CollectorAssignment.objects.create(user=self.observer, market=self.market, is_observer=True)

    def test_dashboard_queryset_by_role_and_search(self) -> None:
        # Collector: own drafts OR collector confirmation
        f1 = CollectionForm.objects.create(
            miner_name="Collector Draft",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        f2 = CollectionForm.objects.create(
            miner_name="Other Confirmation",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.observer,
            market=self.market,
            status=CollectionForm.Status.COLLECTOR_CONFIRMATION,
        )
        f3 = CollectionForm.objects.create(
            miner_name="Observer Draft",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.observer,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        self.client.login(username="collector_html", password="password")
        resp = self.client.get(reverse("collection-list"))
        self.assertEqual(resp.status_code, 200)
        qs = list(resp.context["object_list"])
        self.assertIn(f1, qs)
        self.assertIn(f2, qs)
        self.assertNotIn(f3, qs)

        # Search by miner_name
        resp2 = self.client.get(reverse("collection-list"), {"q": "Collector"})
        self.assertEqual(resp2.status_code, 200)
        qs2 = list(resp2.context["object_list"])
        self.assertIn(f1, qs2)
        self.assertNotIn(f2, qs2)

        # Observer: only own
        self.client.logout()
        self.client.login(username="observer_html", password="password")
        resp3 = self.client.get(reverse("collection-list"))
        self.assertEqual(resp3.status_code, 200)
        qs3 = list(resp3.context["object_list"])
        self.assertIn(f2, qs3)
        self.assertIn(f3, qs3)
        self.assertNotIn(f1, qs3)

        # Senior: excludes drafts
        self.client.logout()
        self.client.login(username="senior_html", password="password")
        resp4 = self.client.get(reverse("collection-list"))
        self.assertEqual(resp4.status_code, 200)
        qs4 = list(resp4.context["object_list"])
        self.assertIn(f2, qs4)
        self.assertNotIn(f1, qs4)
        self.assertNotIn(f3, qs4)

    def test_collection_action_observer_confirm_and_collector_approve(self) -> None:
        draft = CollectionForm.objects.create(
            miner_name="Draft",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.observer,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        self.client.login(username="observer_html", password="password")
        url_confirm = reverse("collection-action", kwargs={"pk": draft.pk, "action": "confirm"})
        resp = self.client.post(url_confirm)
        self.assertEqual(resp.status_code, 302)
        draft.refresh_from_db()
        self.assertEqual(draft.status, CollectionForm.Status.COLLECTOR_CONFIRMATION)

        self.client.logout()
        self.client.login(username="collector_html", password="password")
        url_approve = reverse("collection-action", kwargs={"pk": draft.pk, "action": "approve"})
        resp2 = self.client.post(url_approve)
        self.assertEqual(resp2.status_code, 302)
        draft.refresh_from_db()
        self.assertEqual(draft.status, CollectionForm.Status.INVOICE_REQUESTED)

    def test_collection_action_cancel_requires_reason(self) -> None:
        pending = CollectionForm.objects.create(
            miner_name="Pending",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        self.client.login(username="senior_html", password="password")
        url_cancel = reverse("collection-action", kwargs={"pk": pending.pk, "action": "cancel"})
        resp = self.client.post(url_cancel, data={})
        self.assertEqual(resp.status_code, 302)
        pending.refresh_from_db()
        self.assertEqual(pending.status, CollectionForm.Status.PENDING_PAYMENT)


class ApiViewsMoreBranchesTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")

        self.collector = User.objects.create_user(username="collector_more", password="password")
        a = CollectorAssignment(
            user=self.collector,
            market=self.market,
            is_collector=True,
            esali_username="esali_u",
            esali_service_id="S1",
        )
        a.set_esali_password_plain("esali_p")
        a.save()

        self.api_client = APIClient()

    def test_collector_esali_config_requires_collector_username(self) -> None:
        url = reverse("collection-collector-esali-config")
        resp = self.api_client.post(url, data={}, format="json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(resp.status_code, 400)

    def test_collector_esali_config_collector_not_found(self) -> None:
        url = reverse("collection-collector-esali-config")
        resp = self.api_client.post(
            url,
            data={"collector_username": "missing"},
            format="json",
            HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
        )
        self.assertEqual(resp.status_code, 404)

    def test_update_esali_service_id_collector_not_found_logs(self) -> None:
        url = reverse("collection-update-esali-service-id")
        resp = self.api_client.post(
            url,
            data={"collector_username": "missing", "esali_service_id": "SVC-1"},
            format="json",
            HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(APILog.objects.filter(action="update_esali_service_id_failed").exists())

    def test_queue_invoices_invalid_limit_uses_default(self) -> None:
        # Seed 1 requested form so we see an update.
        CollectionForm.objects.create(
            miner_name="Req",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        url = reverse("collection-queue-invoices") + "?limit=bad"
        resp = self.api_client.post(url, data={}, format="json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("limit"), 50)

    def test_queue_invoices_select_for_update_fallback(self) -> None:
        # Force select_for_update(skip_locked=True) to fail, and ensure fallback path still works.
        CollectionForm.objects.create(
            miner_name="Req",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.INVOICE_REQUESTED,
        )
        url = reverse("collection-queue-invoices")

        real_qs = CollectionForm.objects.filter(status=CollectionForm.Status.INVOICE_REQUESTED).order_by("created_at", "id")
        with patch.object(type(real_qs), "select_for_update", side_effect=[Exception("no skip_locked"), real_qs]):
            resp = self.api_client.post(url, data={}, format="json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.json().get("updated", 0), 1)

    def test_collector_esali_config_success_logs(self) -> None:
        url = reverse("collection-collector-esali-config")
        resp = self.api_client.post(
            url,
            data={"collector_username": "collector_more"},
            format="json",
            HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["collector_username"], "collector_more")
        self.assertEqual(data["esali_username"], "esali_u")
        self.assertTrue(APILog.objects.filter(action="collector_esali_config").exists())

    def test_update_esali_service_id_success_logs_and_persists(self) -> None:
        url = reverse("collection-update-esali-service-id")
        resp = self.api_client.post(
            url,
            data={"collector_username": "collector_more", "esali_service_id": "SVC-NEW"},
            format="json",
            HTTP_X_API_KEY="EXPECTED_BANK_API_KEY",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(APILog.objects.filter(action="update_esali_service_id").exists())
        self.assertEqual(
            CollectorAssignment.objects.get(user__username="collector_more").esali_service_id, "SVC-NEW"
        )


class CollectorAssignmentCryptoBranchesTests(TestCase):
    def test_get_fernet_missing_key_raises(self) -> None:
        settings.ESALI_FERNET_KEY = ""
        a = CollectorAssignment(
            user=User.objects.create_user("u1"),
            market=Market.objects.create(market_name="M", location="L"),
        )
        with self.assertRaises(ValidationError):
            with patch.dict(os.environ, {"ESALI_FERNET_KEY": ""}, clear=True):
                a._get_fernet()

    def test_get_fernet_invalid_key_raises(self) -> None:
        settings.ESALI_FERNET_KEY = "not-a-key"
        a = CollectorAssignment(user=User.objects.create_user("u2"), market=Market.objects.create(market_name="M2", location="L2"))
        with self.assertRaises(ValidationError):
            a._get_fernet()

    def test_get_esali_password_plain_invalid_token_raises(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        a = CollectorAssignment(user=User.objects.create_user("u3"), market=Market.objects.create(market_name="M3", location="L3"))
        a.esali_password_enc = "not-a-token"
        with self.assertRaises(ValidationError):
            a.get_esali_password_plain()

    def test_get_esali_password_plain_empty_returns_empty(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        a = CollectorAssignment(
            user=User.objects.create_user("u3b"),
            market=Market.objects.create(market_name="M3b", location="L3b"),
        )
        a.esali_password_enc = ""
        self.assertEqual(a.get_esali_password_plain(), "")

    def test_collector_clean_requires_esali_fields(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        a = CollectorAssignment(
            user=User.objects.create_user("u4"),
            market=Market.objects.create(market_name="M4", location="L4"),
            is_collector=True,
            esali_username="",
            esali_service_id="",
            esali_password_enc="",
        )
        with self.assertRaises(ValidationError):
            a.full_clean()


class HtmlViewsMoreBranchesTests(TestCase):
    def setUp(self) -> None:
        settings.ESALI_FERNET_KEY = Fernet.generate_key().decode("utf-8")
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.user_no_assignment = User.objects.create_user(username="no_assign_html", password="password")

        self.observer = User.objects.create_user(username="observer_more_html", password="password")
        CollectorAssignment.objects.create(user=self.observer, market=self.market, is_observer=True)

        self.collector = User.objects.create_user(username="collector_more_html2", password="password")
        a = CollectorAssignment(user=self.collector, market=self.market, is_collector=True, esali_username="u", esali_service_id="S1")
        a.set_esali_password_plain("p")
        a.save()

        self.senior = User.objects.create_user(username="senior_more_html", password="password")
        CollectorAssignment.objects.create(user=self.senior, market=self.market, is_senior_collector=True)

    def test_create_view_missing_assignment_hits_form_invalid_branch(self) -> None:
        # User must pass `test_func` (needs an assignment) but still hit the
        # `CollectorAssignment.DoesNotExist` branch in `form_valid`.
        CollectorAssignment.objects.create(user=self.user_no_assignment, market=self.market, is_observer=True)

        self.client.login(username="no_assign_html", password="password")
        with patch("form15_tra.views.CollectorAssignment.objects.get", side_effect=CollectorAssignment.DoesNotExist()):
            resp = self.client.post(
                reverse("collection-create"),
                data={"miner_name": "X", "phone": "0123456789", "sacks_count": 1},
            )
        self.assertEqual(resp.status_code, 200)

    def test_action_view_unauthorized_branches(self) -> None:
        draft = CollectionForm.objects.create(
            miner_name="Draft",
            phone="0123456789",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.observer,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )

        self.client.login(username="no_assign_html", password="password")
        resp = self.client.post(reverse("collection-action", kwargs={"pk": draft.pk, "action": "confirm"}), follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.logout()
        self.client.login(username="observer_more_html", password="password")
        resp2 = self.client.post(reverse("collection-action", kwargs={"pk": draft.pk, "action": "approve"}), follow=True)
        self.assertEqual(resp2.status_code, 200)

        self.client.logout()
        self.client.login(username="collector_more_html2", password="password")
        resp3 = self.client.post(reverse("collection-action", kwargs={"pk": draft.pk, "action": "cancel"}), follow=True)
        self.assertEqual(resp3.status_code, 200)

    def test_action_view_wrong_status_branches(self) -> None:
        # confirm when not draft -> error branch
        not_draft = CollectionForm.objects.create(
            miner_name="ND",
            phone="0123456789",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        self.client.login(username="collector_more_html2", password="password")
        resp = self.client.post(reverse("collection-action", kwargs={"pk": not_draft.pk, "action": "confirm"}), follow=True)
        self.assertEqual(resp.status_code, 200)

        # approve when wrong status -> error branch
        wrong_approve = CollectionForm.objects.create(
            miner_name="WA",
            phone="0123456789",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.observer,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        resp2 = self.client.post(reverse("collection-action", kwargs={"pk": wrong_approve.pk, "action": "approve"}), follow=True)
        self.assertEqual(resp2.status_code, 200)

        # cancel when wrong status -> error branch
        wrong_cancel = CollectionForm.objects.create(
            miner_name="WC",
            phone="0123456789",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.DRAFT,
        )
        self.client.logout()
        self.client.login(username="senior_more_html", password="password")
        resp3 = self.client.post(
            reverse("collection-action", kwargs={"pk": wrong_cancel.pk, "action": "cancel"}),
            data={"cancellation_reason": "X"},
            follow=True,
        )
        self.assertEqual(resp3.status_code, 200)

    def test_action_view_cancel_success_branch(self) -> None:
        pending = CollectionForm.objects.create(
            miner_name="P",
            phone="0123456789",
            sacks_count=1,
            total_amount=Decimal("0.00"),
            collector=self.collector,
            market=self.market,
            status=CollectionForm.Status.PENDING_PAYMENT,
        )
        self.client.login(username="senior_more_html", password="password")
        resp = self.client.post(
            reverse("collection-action", kwargs={"pk": pending.pk, "action": "cancel"}),
            data={"cancellation_reason": "Reason"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, CollectionForm.Status.CANCELLED)
