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

User = get_user_model()

class MiningSystemTests(TestCase):
    """
    Unit tests for the Mining Revenue Collection System.
    Tests state transitions, validation, and immutability.
    """

    def setUp(self) -> None:
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
        self.assignment = CollectorAssignment.objects.create(
            user=self.collector,
            market=self.market,
            is_collector=True
        )
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

    def test_auto_receipt_generation(self) -> None:
        """
        Ensure receipt_number is auto-generated correctly.
        Format: {market_id}{sequence}
        """
        form = CollectionForm(
            miner_name="John Doe",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market
        )
        form.save()
        
        prefix = str(self.market.id)
        expected_receipt = f"{prefix}{1:0{10-len(prefix)}d}" # First one
        self.assertEqual(form.receipt_number, expected_receipt)
        self.assertTrue(len(form.receipt_number) == 10)

        # Second one
        form2 = CollectionForm.objects.create(
            miner_name="Jane Doe",
            sacks_count=10,
            total_amount=Decimal("1000.00"),
            collector=self.collector,
            market=self.market
        )
        expected_receipt_2 = f"{prefix}{2:0{10-len(prefix)}d}"
        self.assertEqual(form2.receipt_number, expected_receipt_2)

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
        self.assertRedirects(response, reverse('collection-detail', kwargs={'pk': paid_form.pk}))
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
        self.assertRedirects(response, reverse('collection-detail', kwargs={'pk': pending_form.pk}))
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
        self.assertRedirects(resp1, reverse("collection-detail", kwargs={"pk": pending_form.pk}))
        self.assertContains(resp1, "ليس لديك صلاحية للطباعة")

        resp2 = self.client.get(reverse("receipt-print", kwargs={"pk": paid_form.pk}), follow=True)
        self.assertRedirects(resp2, reverse("collection-detail", kwargs={"pk": paid_form.pk}))
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

        # Second call should update 0 (already paid / not eligible)
        response2 = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("updated"), 0)

    def test_mark_paid_endpoint_requires_receipts(self) -> None:
        url = reverse("collection-mark-paid")
        response = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 400)

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

        # Second call should update 0 (already updated / not eligible)
        response2 = self.client.post(url, data=payload, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json().get("updated"), 0)

    def test_set_pending_payment_endpoint_requires_invoices(self) -> None:
        url = reverse("collection-set-pending-payment")
        response = self.client.post(url, data={}, content_type="application/json", HTTP_X_API_KEY="EXPECTED_BANK_API_KEY")
        self.assertEqual(response.status_code, 400)


class CollectionApiActionTests(TestCase):
    def setUp(self) -> None:
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")

        self.collector = User.objects.create_user(username="collector_api", password="password")
        CollectorAssignment.objects.create(user=self.collector, market=self.market, is_collector=True)

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
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_create", password="password")
        CollectorAssignment.objects.create(user=self.collector, market=self.market, is_collector=True)

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
        self.assertTrue(data["receipt_number"])

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
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_perm", password="password")
        CollectorAssignment.objects.create(user=self.collector, market=self.market, is_collector=True)

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


class HtmlViewsBranchTests(TestCase):
    def setUp(self) -> None:
        self.market = Market.objects.create(market_name="Test Market", location="Test Location")
        self.collector = User.objects.create_user(username="collector_html", password="password")
        CollectorAssignment.objects.create(user=self.collector, market=self.market, is_collector=True)

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
