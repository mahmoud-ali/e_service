import os
import runpy
import sqlite3
import time
import tempfile
import unittest
from dataclasses import dataclass
from typing import Any

import httpx
from unittest import mock

from form15_tra.cli import sync_e15
from form15_tra.cli.lib import esali_api as esali_api_mod

# These tests target the standalone CLI worker and are intended to be run via:
# `python -m unittest form15_tra.cli.tests`
#
# When you run `python manage.py test form15_tra`, Django's test discovery will
# also find this module because it's under the `form15_tra` package tree.
# That makes the Django test output noisy (intentional logs/tracebacks in CLI tests).
#
# When running Django's test runner (manage.py test), we skip this module so it
# doesn't run twice / spam logs. We detect Django-runner by the env var it sets.
if os.getenv("DJANGO_SETTINGS_MODULE"):
    raise unittest.SkipTest("Skip CLI unit tests under Django test runner (run via unittest instead).")


@dataclass
class _FakeResponse:
    status_code: int
    _json: Any
    text: str = ""

    def json(self) -> Any:
        return self._json


class _FakeAsyncClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._queue: list[_FakeResponse] = []

    def enqueue(self, resp: _FakeResponse) -> None:
        self._queue.append(resp)

    async def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self._queue:
            raise RuntimeError("No queued fake responses")
        return self._queue.pop(0)


class _FakeAsyncClientCM:
    def __init__(self, inner: Any) -> None:
        self._inner = inner

    async def __aenter__(self) -> Any:
        return self._inner

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class SyncE15Tests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._old_argv = list(os.sys.argv)
        self._old_env = dict(os.environ)

    def tearDown(self) -> None:
        os.sys.argv = self._old_argv
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_helpers_env_int_float_normalize_and_backoff(self) -> None:
        self.assertEqual(sync_e15._env_int("MISSING_INT", 7), 7)
        self.assertEqual(sync_e15._env_float("MISSING_FLOAT", 1.5), 1.5)
        os.environ["X_INT"] = "not-an-int"
        os.environ["X_FLOAT"] = "not-a-float"

        self.assertEqual(sync_e15._env_int("X_INT", 7), 7)
        self.assertEqual(sync_e15._env_float("X_FLOAT", 1.5), 1.5)
        self.assertEqual(sync_e15._normalize_base_url("http://a/b/"), "http://a/b")

        with mock.patch.object(sync_e15.random, "random", return_value=0.0):
            self.assertGreater(sync_e15._backoff_sleep_s(0, base=0.25, cap=5.0), 0)
            self.assertLessEqual(sync_e15._backoff_sleep_s(999, base=0.25, cap=1.0), 1.0)

    async def test_other_service_client_base_raises(self) -> None:
        base = sync_e15.E15Client()
        with self.assertRaises(NotImplementedError):
            await base.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1,
                    miner_name="a",
                    phone="",
                    total_amount=1,
                    market_name="m",
                    collector_username="c",
                )
            )
        with self.assertRaises(NotImplementedError):
            await base.check_paid("inv1")

    async def test_mock_other_service_is_deterministic(self) -> None:
        e15 = sync_e15.MockE15Client()
        item = sync_e15.QueuedInvoice(
            id=123, miner_name="A", phone="", total_amount=10, market_name="M1", collector_username="c"
        )

        r1 = await e15.create_invoice(item)
        r2 = await e15.create_invoice(item)

        self.assertEqual(r1.id, 123)
        self.assertEqual(r1.invoice_id, r2.invoice_id)
        self.assertTrue(r1.invoice_id.startswith("MOCK-123-"))

    async def test_mock_other_service_check_paid_returns_receipt_when_paid(self) -> None:
        e15 = sync_e15.MockE15Client()
        paid, receipt = await e15.check_paid("inv-test")
        self.assertIsInstance(paid, bool)
        if paid:
            self.assertTrue(receipt)

    async def test_parallel_create_invoices_returns_all_successes(self) -> None:
        e15 = sync_e15.MockE15Client()
        items = [
            sync_e15.QueuedInvoice(id=1, miner_name="a", phone="", total_amount=1, market_name="m", collector_username="c"),
            sync_e15.QueuedInvoice(id=2, miner_name="b", phone="", total_amount=2, market_name="m", collector_username="c"),
            sync_e15.QueuedInvoice(id=3, miner_name="c", phone="", total_amount=3, market_name="m", collector_username="c"),
        ]
        results = await sync_e15._run_parallel_create_invoices(e15, items, concurrency=2)
        self.assertEqual(sorted(r.id for r in results), [1, 2, 3])

    async def test_parallel_create_invoices_omits_failures(self) -> None:
        class _FlakyE15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                if item.id == 2:
                    raise RuntimeError("boom")
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

        items = [
            sync_e15.QueuedInvoice(id=1, miner_name="a", phone="", total_amount=1, market_name="m", collector_username="c"),
            sync_e15.QueuedInvoice(id=2, miner_name="b", phone="", total_amount=2, market_name="m", collector_username="c"),
            sync_e15.QueuedInvoice(id=3, miner_name="c", phone="", total_amount=3, market_name="m", collector_username="c"),
        ]
        results = await sync_e15._run_parallel_create_invoices(_FlakyE15(), items, concurrency=3)
        self.assertEqual(sorted(r.id for r in results), [1, 3])

    async def test_request_with_retries_retries_transient_errors(self) -> None:
        attempts: list[int] = []

        async def flaky() -> str:
            attempts.append(1)
            if len(attempts) < 3:
                raise httpx.TransportError("temporary")
            return "ok"

        out = await sync_e15._request_with_retries(flaky, attempts=5)
        self.assertEqual(out, "ok")
        self.assertEqual(len(attempts), 3)

    async def test_request_with_retries_exhausts_and_raises(self) -> None:
        async def always_fail() -> str:
            raise httpx.TimeoutException("nope")

        with mock.patch.object(sync_e15, "_backoff_sleep_s", return_value=0.0):
            with self.assertRaises(httpx.TimeoutException):
                await sync_e15._request_with_retries(always_fail, attempts=2)

    async def test_e15_queue_invoices_parses_results_list(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(
            _FakeResponse(
                status_code=200,
                _json={
                    "updated": 2,
                    "limit": 50,
                    "returned": 2,
                    "results": [
                        {"id": 10, "miner_name": "x", "phone": "0123456789", "total_amount": 100, "market_name": "mk", "collector_username": "c1"},
                        {"id": "11", "miner_name": "y", "phone": "", "total_amount": "200", "market_name": "mk2", "collector_username": "c2"},
                    ],
                },
            )
        )

        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        items = await smrc.queue_invoices(fake, limit=50)  # type: ignore[arg-type]

        self.assertEqual([i.id for i in items], [10, 11])
        self.assertEqual(items[0].market_name, "mk")
        self.assertEqual(items[0].phone, "0123456789")
        self.assertEqual(items[0].collector_username, "c1")
        self.assertEqual(fake.calls[0]["params"]["limit"], 50)
        self.assertEqual(fake.calls[0]["headers"]["X-API-KEY"], "k")

    async def test_e15_queue_invoices_skips_malformed_rows(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(
            _FakeResponse(
                status_code=200,
                _json={"results": [{"id": 1, "miner_name": "ok", "phone": "0", "total_amount": 1, "market_name": "m", "collector_username": "c"}, {"bad": "row"}]},
            )
        )
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        items = await smrc.queue_invoices(fake, limit=50)  # type: ignore[arg-type]
        self.assertEqual([i.id for i in items], [1])

    async def test_e15_queue_invoices_skips_non_dict_missing_and_empty_and_bad_id(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(
            _FakeResponse(
                status_code=200,
                _json={
                    "results": [
                        "not-a-dict",
                        {"miner_name": "missing-id"},
                        {"id": "   ", "miner_name": "empty-id"},
                        {
                            "id": "not-an-int",
                            "miner_name": "bad-int",
                            "phone": "0",
                            "total_amount": 1,
                            "market_name": "m",
                            "collector_username": "c",
                        },
                        {
                            "id": 2,
                            "miner_name": "ok",
                            "phone": "0",
                            "total_amount": 1,
                            "market_name": "m",
                            "collector_username": "c",
                        },
                    ]
                },
            )
        )
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        items = await smrc.queue_invoices(fake, limit=50)  # type: ignore[arg-type]
        self.assertEqual([i.id for i in items], [2])

    async def test_e15_queue_invoices_non_200_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=500, _json={"x": 1}, text="boom"))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.queue_invoices(fake, limit=1)  # type: ignore[arg-type]

    async def test_e15_set_pending_payment_builds_expected_payload(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json={"requested": 2, "updated": 2, "skipped": 0}))

        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        resp = await smrc.set_pending_payment(
            fake,  # type: ignore[arg-type]
            [
                sync_e15.E15Result(id=1, invoice_id="inv1"),
                sync_e15.E15Result(id=2, invoice_id="inv2"),
            ],
        )
        self.assertEqual(resp["updated"], 2)
        self.assertEqual(
            fake.calls[0]["json"],
            {"invoices": [{"id": 1, "invoice_id": "inv1"}, {"id": 2, "invoice_id": "inv2"}]},
        )

    async def test_e15_set_pending_payment_empty_short_circuits(self) -> None:
        fake = _FakeAsyncClient()
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        out = await smrc.set_pending_payment(fake, [])  # type: ignore[arg-type]
        self.assertEqual(out["requested"], 0)
        self.assertEqual(fake.calls, [])

    async def test_e15_set_pending_payment_non_200_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=400, _json={"x": 1}, text="bad"))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.set_pending_payment(
                fake,  # type: ignore[arg-type]
                [sync_e15.E15Result(id=1, invoice_id="inv1")],
            )

    async def test_e15_mark_paid_filters_missing_receipt_numbers(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json={"requested": 1, "updated": 1, "skipped": 0}))

        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        resp = await smrc.mark_paid(
            fake,  # type: ignore[arg-type]
            [
                sync_e15.E15Result(id=1, invoice_id="inv1", receipt_number="r1"),
                sync_e15.E15Result(id=2, invoice_id="inv2", receipt_number=None),
                sync_e15.E15Result(id=3, invoice_id="inv3", receipt_number=""),
            ],
        )
        self.assertEqual(resp["updated"], 1)
        self.assertEqual(fake.calls[0]["json"], {"receipts": [{"id": 1, "receipt_number": "r1"}]})

    async def test_e15_mark_paid_includes_rrn_when_present(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json={"requested": 1, "updated": 1, "skipped": 0}))

        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        await smrc.mark_paid(
            fake,  # type: ignore[arg-type]
            [
                sync_e15.E15Result(id=1, invoice_id="inv1", receipt_number="r1", rrn_number="RRN1"),
            ],
        )
        self.assertEqual(
            fake.calls[0]["json"],
            {"receipts": [{"id": 1, "receipt_number": "r1", "rrn_number": "RRN1"}]},
        )

    async def test_e15_mark_paid_empty_short_circuits(self) -> None:
        fake = _FakeAsyncClient()
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        out = await smrc.mark_paid(fake, [])  # type: ignore[arg-type]
        self.assertEqual(out["requested"], 0)
        self.assertEqual(fake.calls, [])

    async def test_e15_mark_paid_non_200_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=500, _json={"x": 1}, text="err"))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.mark_paid(
                fake,  # type: ignore[arg-type]
                [sync_e15.E15Result(id=1, invoice_id="inv1", receipt_number="r1")],
            )

    def test_parse_args_requires_api_key(self) -> None:
        os.sys.argv = ["sync_e15"]
        os.environ.pop("SMRC_API_KEY", None)
        with self.assertRaises(SystemExit):
            sync_e15._parse_args()

    def test_parse_args_clamps_and_env_mark_paid(self) -> None:
        os.environ["SMRC_API_KEY"] = "k"
        os.environ["ENABLE_MARK_PAID"] = "1"
        os.sys.argv = [
            "sync_e15",
            "--limit",
            "9999",
            "--concurrency",
            "0",
            "--idle-sleep-s",
            "0",
            "--timeout-s",
            "0",
            "--mark-paid-sleep-s",
            "0",
            "--mark-paid-jitter-pct",
            "2",
        ]
        s = sync_e15._parse_args()
        self.assertEqual(s.limit, 500)
        self.assertEqual(s.concurrency, 1)
        self.assertEqual(s.idle_sleep_s, 0.1)
        self.assertEqual(s.timeout_s, 1.0)
        self.assertTrue(s.enable_mark_paid)
        self.assertEqual(s.mark_paid_sleep_s, 1.0)
        self.assertEqual(s.mark_paid_jitter_pct, 1.0)
        self.assertEqual(s.mark_paid_first_check_delay_s, 60.0)
        self.assertEqual(s.mark_paid_check_max_delay_s, 3600.0)
        self.assertIsNotNone(s.esali_base_url)
        self.assertEqual(s.esali_timeout_s, 60.0)

    async def test_run_daemon_non_mock_mode_exits(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="real",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )
        with self.assertRaises(SystemExit):
            await sync_e15.run_daemon(settings)

    async def test_esali_client_login_cached_and_create_invoice_and_check_paid(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                self.login_calls = 0
                self.invoice_calls: list[dict[str, Any]] = []
                self.receipt_calls: list[str] = []

            def login_user(self) -> dict[str, Any]:
                self.login_calls += 1
                return {"CenterId": "CID-1"}

            def get_invoice_more_services(
                self,
                services: list[dict[str, Any]],
                customer_name: str,
                center_id: str,
                payment_method_id: str,
                phone: str,
                total_amount: float,
                note: str = "",
            ) -> dict[str, Any]:
                self.invoice_calls.append(
                    {
                        "services": services,
                        "customer_name": customer_name,
                        "center_id": center_id,
                        "payment_method_id": payment_method_id,
                        "phone": phone,
                        "total_amount": total_amount,
                        "note": note,
                    }
                )
                return {"InvoiceNo": "INV-123"}

            def get_receipt(self, invoice_number: str) -> dict[str, Any]:
                self.receipt_calls.append(invoice_number)
                return {"LOCALRECEIPTNO": "RCP-9", "RRN": "RRN-9"}

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
                note="n",
            )

            res = await c.create_invoice(
                sync_e15.QueuedInvoice(
                    id=7,
                    miner_name="Ahmed",
                    phone="0123456789",
                    total_amount=10,
                    market_name="m",
                    collector_username="collector1",
                )
            )
            self.assertEqual(res.invoice_id, "INV-123")

            paid, receipt, rrn = await c.check_paid_for_collector("INV-123", "collector1")
            self.assertTrue(paid)
            self.assertEqual(receipt, "RCP-9")
            self.assertEqual(rrn, "RRN-9")

    async def test_esali_client_check_paid_unpaid_code_01_returns_false(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_receipt(self, invoice_number: str) -> dict[str, Any]:
                raise sync_e15.EsaliAPIError("01", "Invoice No Data found OR Unpaid")

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
                note="",
            )
            paid, receipt, rrn = await c.check_paid_for_collector("INV-X", "collector1")
            self.assertFalse(paid)
            self.assertIsNone(receipt)
            self.assertIsNone(rrn)

    async def test_esali_client_check_paid_missing_receipt_fields_returns_false(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_receipt(self, invoice_number: str) -> dict[str, Any]:
                return {"x": invoice_number}

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
                note="",
            )
            paid, receipt, rrn = await c.check_paid_for_collector("INV-X", "collector1")
            self.assertFalse(paid)
            self.assertIsNone(receipt)
            self.assertIsNone(rrn)

    async def test_esali_client_check_paid_other_error_propagates(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_receipt(self, invoice_number: str) -> dict[str, Any]:
                raise sync_e15.EsaliAPIError("06", "Internal Error")

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
            )
            with self.assertRaises(sync_e15.EsaliAPIError):
                await c.check_paid_for_collector("INV-X", "collector1")

    async def test_esali_client_get_services_normalizes_non_list_to_empty(self) -> None:
        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        c = sync_e15.EsaliClient(
            base_url="https://x/api/",
            api_key="k",
            timeout_s=60.0,
            payment_method_id="6",
            get_collector_config=get_cfg,
        )

        class _Api:
            def get_services(self) -> Any:
                return {"x": 1}

        with mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)):
            out = await c.get_services(_Api())  # type: ignore[arg-type]
            self.assertEqual(out, [])

    async def test_esali_client_get_services_returns_list(self) -> None:
        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        c = sync_e15.EsaliClient(
            base_url="https://x/api/",
            api_key="k",
            timeout_s=60.0,
            payment_method_id="6",
            get_collector_config=get_cfg,
        )

        class _Api:
            def get_services(self) -> Any:
                return [{"ServiceId": "S1"}]

        with mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)):
            out = await c.get_services(_Api())  # type: ignore[arg-type]
            self.assertEqual(out, [{"ServiceId": "S1"}])

    async def test_esali_client_login_center_id_non_dict_raises(self) -> None:
        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u",
                esali_password_plain="p",
                esali_service_id="S1",
            )

        c = sync_e15.EsaliClient(
            base_url="https://x/api/",
            api_key="k",
            timeout_s=60.0,
            payment_method_id="6",
            get_collector_config=get_cfg,
        )

        class _Api:
            def login_user(self) -> Any:
                return "not-a-dict"

        with mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)):
            with self.assertRaises(sync_e15.EsaliAPIError):
                await c._login_center_id(_Api())  # type: ignore[arg-type]

    def test_extract_receipt_number_supports_dict_list_and_alt_keys(self) -> None:
        self.assertIsNone(sync_e15._extract_receipt_number([]))
        self.assertIsNone(sync_e15._extract_receipt_number(object()))
        self.assertIsNone(sync_e15._extract_receipt_number({"x": 1}))
        self.assertEqual(sync_e15._extract_receipt_number({"ReceiptNo": "R1"}), "R1")
        self.assertEqual(sync_e15._extract_receipt_number([{"LOCALRECEIPTNO": "R2"}]), "R2")

    def test_extract_rrn_number_supports_dict_list_and_missing(self) -> None:
        self.assertIsNone(sync_e15._extract_rrn_number([]))
        self.assertIsNone(sync_e15._extract_rrn_number(object()))
        self.assertIsNone(sync_e15._extract_rrn_number({"x": 1}))
        self.assertEqual(sync_e15._extract_rrn_number({"RRN": "X1"}), "X1")
        self.assertEqual(sync_e15._extract_rrn_number([{"RRN": "X2"}]), "X2")

    def test_decrypt_esali_password_round_trip(self) -> None:
        key = sync_e15.Fernet.generate_key()
        token = sync_e15.Fernet(key).encrypt(b"pw").decode("utf-8")
        with mock.patch.dict(os.environ, {"ESALI_FERNET_KEY": key.decode("utf-8")}, clear=False):
            self.assertEqual(sync_e15._decrypt_esali_password(token), "pw")
            self.assertEqual(sync_e15._decrypt_esali_password(""), "")

        with mock.patch.dict(os.environ, {"ESALI_FERNET_KEY": ""}, clear=False):
            with self.assertRaises(RuntimeError):
                sync_e15._decrypt_esali_password(token)

        with mock.patch.dict(os.environ, {"ESALI_FERNET_KEY": key.decode("utf-8")}, clear=False):
            with self.assertRaises(RuntimeError):
                sync_e15._decrypt_esali_password("not-a-token")

    async def test_smrc_get_collector_esali_config_builds_expected_payload(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(
            _FakeResponse(
                status_code=200,
                _json={
                    "collector_username": "collector1",
                    "esali_username": "u",
                    "esali_password_enc": "enc",
                    "esali_service_id": "S1",
                },
            )
        )
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        out = await smrc.get_collector_esali_config(fake, "collector1")  # type: ignore[arg-type]
        self.assertEqual(out["esali_service_id"], "S1")
        self.assertEqual(fake.calls[0]["json"], {"collector_username": "collector1"})

    async def test_smrc_get_collector_esali_config_non_200_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=500, _json={"x": 1}, text="boom"))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.get_collector_esali_config(fake, "collector1")  # type: ignore[arg-type]

    async def test_smrc_get_collector_esali_config_non_dict_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json=["x"]))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.get_collector_esali_config(fake, "collector1")  # type: ignore[arg-type]

    async def test_smrc_update_esali_service_id_non_dict_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json=["x"]))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.update_esali_service_id(  # type: ignore[arg-type]
                fake, {"collector_username": "collector1", "esali_service_id": "S1"}
            )

    async def test_smrc_update_esali_service_id_non_200_raises(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=500, _json={"x": 1}, text="boom"))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        with self.assertRaises(sync_e15.E15APIError):
            await smrc.update_esali_service_id(  # type: ignore[arg-type]
                fake, {"collector_username": "collector1", "esali_service_id": "S1"}
            )

    async def test_smrc_update_esali_service_id_success_returns_dict(self) -> None:
        fake = _FakeAsyncClient()
        fake.enqueue(_FakeResponse(status_code=200, _json={"collector_username": "collector1", "esali_service_id": "S1"}))
        smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
        out = await smrc.update_esali_service_id(  # type: ignore[arg-type]
            fake, {"collector_username": "collector1", "esali_service_id": "S1"}
        )
        self.assertEqual(out["esali_service_id"], "S1")

    def test_sqlite_init_db_backfills_phone_column(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            conn = sqlite3.connect(db_path)
            try:
                # Simulate older schema without `phone`
                conn.execute(
                    """
                    CREATE TABLE e15_sync_invoices (
                        collection_id INTEGER PRIMARY KEY,
                        miner_name TEXT,
                        total_amount TEXT,
                        market_name TEXT,
                        status TEXT NOT NULL,
                        invoice_id TEXT NULL,
                        receipt_number TEXT NULL,
                        queued_at INTEGER,
                        invoice_generated_at INTEGER NULL,
                        pending_payment_sent_at INTEGER NULL,
                        paid_at INTEGER NULL,
                        last_error TEXT NULL,
                        updated_at INTEGER NOT NULL
                    )
                    """
                )
            finally:
                conn.close()

            store = sync_e15.SQLiteStore(db_path)
            store.init_db()

            conn2 = sqlite3.connect(db_path)
            try:
                cols = {r[1] for r in conn2.execute("PRAGMA table_info(e15_sync_invoices)").fetchall()}
                self.assertIn("phone", cols)
                self.assertIn("collector_username", cols)
            finally:
                conn2.close()

    async def test_esali_client_ensure_logged_in_missing_centerid_raises(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": ""}

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u", esali_password_plain="p", esali_service_id="S1"
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
            )
            with self.assertRaises(sync_e15.EsaliAPIError):
                await c.create_invoice(
                    sync_e15.QueuedInvoice(
                        id=1,
                        miner_name="n",
                        phone="0123456789",
                        total_amount=1,
                        market_name="m",
                        collector_username="collector1",
                    )
                )

    async def test_esali_client_create_invoice_missing_invoiceno_raises(self) -> None:
        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_invoice_more_services(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
                return {"x": 1}

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u", esali_password_plain="p", esali_service_id="S1"
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
            )
            with self.assertRaises(sync_e15.EsaliAPIError):
                await c.create_invoice(
                    sync_e15.QueuedInvoice(
                        id=1,
                        miner_name="n",
                        phone="0123456789",
                        total_amount=1,
                        market_name="m",
                        collector_username="collector1",
                    )
                )

    async def test_esali_client_map_item_bad_amount_falls_back_to_zero(self) -> None:
        seen: dict[str, Any] = {}

        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_invoice_more_services(
                self,
                services: list[dict[str, Any]],
                customer_name: str,
                center_id: str,
                payment_method_id: str,
                phone: str,
                total_amount: float,
                note: str = "",
            ) -> dict[str, Any]:
                seen["services"] = services
                seen["total_amount"] = total_amount
                return {"InvoiceNo": "INV-0"}

        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u", esali_password_plain="p", esali_service_id="S1"
            )

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
        ):
            c = sync_e15.EsaliClient(
                base_url="https://x/api/",
                api_key="k",
                timeout_s=60.0,
                payment_method_id="6",
                get_collector_config=get_cfg,
            )
            await c.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1,
                    miner_name="n",
                    phone="0123456789",
                    total_amount=object(),
                    market_name="m",
                    collector_username="collector1",
                )
            )
            self.assertEqual(seen["total_amount"], 0.0)
            self.assertEqual(seen["services"][0]["amount"], 0.0)

    async def test_esali_client_missing_collector_username_raises_keyerror(self) -> None:
        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u", esali_password_plain="p", esali_service_id="S1"
            )

        c = sync_e15.EsaliClient(
            base_url="https://x/api/",
            api_key="k",
            timeout_s=60.0,
            payment_method_id="6",
            get_collector_config=get_cfg,
        )
        with self.assertRaises(KeyError):
            await c.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1, miner_name="n", phone="0123456789", total_amount=1, market_name="m", collector_username=""
                )
            )

    async def test_esali_client_check_paid_method_raises(self) -> None:
        async def get_cfg(_collector_username: str) -> sync_e15.EsaliCollectorConfig:
            return sync_e15.EsaliCollectorConfig(
                esali_username="u", esali_password_plain="p", esali_service_id="S1"
            )

        c = sync_e15.EsaliClient(
            base_url="https://x/api/",
            api_key="k",
            timeout_s=60.0,
            payment_method_id="6",
            get_collector_config=get_cfg,
        )
        with self.assertRaises(RuntimeError):
            await c.check_paid("INV-1")

    async def test_step_generate_invoices_returns_0_when_external_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=1, miner_name="a", phone="0", total_amount=1, market_name="m", collector_username="c")]
            )
            smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
            fake_http = _FakeAsyncClient()

            with (
                mock.patch.object(sync_e15, "_run_parallel_create_invoices", return_value=[]),
            ):
                out = await sync_e15.step_generate_invoices(
                    smrc, fake_http, sync_e15.MockE15Client(), store, limit=10, concurrency=2  # type: ignore[arg-type]
                )
                self.assertEqual(out, 0)

    async def test_step_mark_paid_returns_0_when_paid_check_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=1, miner_name="a", phone="0", total_amount=1, market_name="m", collector_username="c")]
            )
            store.set_invoice_generated([sync_e15.E15Result(id=1, invoice_id="inv1")], first_check_delay_s=0.0)
            smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
            fake_http = _FakeAsyncClient()

            before_ms = int(time.time() * 1000)
            with (
                mock.patch.object(sync_e15, "_run_parallel_check_paid", return_value=[(1, None)]),
            ):
                out = await sync_e15.step_mark_paid(
                    smrc, fake_http, sync_e15.MockE15Client(), store, limit=10, concurrency=2  # type: ignore[arg-type]
                )
                self.assertEqual(out, 0)
            conn = sqlite3.connect(db_path)
            try:
                row = conn.execute(
                    "SELECT paid_check_retries, paid_check_next_at_ms FROM e15_sync_invoices WHERE collection_id=1"
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(int(row[0]), 1)
                self.assertGreaterEqual(int(row[1]), before_ms + 1500)
            finally:
                conn.close()

    async def test_run_daemon_esali_mode_missing_env_exits(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="esali",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url="",
            esali_api_key="",
            esali_timeout_s=60.0,
            esali_payment_method_id="",
            esali_note="",
        )
        with self.assertRaises(SystemExit):
            await sync_e15.run_daemon(settings)

    async def test_run_daemon_esali_mode_wires_client_and_starts_tasks(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="esali",
            external_base_url=None,
            enable_mark_paid=True,
            esali_base_url="https://x/api/",
            esali_api_key="k2",
            esali_timeout_s=60.0,
            esali_payment_method_id="6",
            esali_note="",
        )

        class _FakeEsaliClient(sync_e15.E15Client):
            def __init__(self, **_kwargs: Any) -> None:
                self.logged_in = 0

            async def ensure_logged_in(self) -> str:
                self.logged_in += 1
                return "CID-1"

            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id="INV-1")

            async def check_paid(self, invoice_id: str) -> tuple[bool, str | None]:
                return False, None

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        async def _fake_gather(*aws: Any) -> None:
            # Actually run the loops once (sleep sets stop_event).
            for aw in aws:
                try:
                    await aw
                except Exception:
                    pass
            return None

        with (
            mock.patch.object(sync_e15, "EsaliClient", _FakeEsaliClient),
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", return_value=0),
            mock.patch.object(sync_e15, "step_generate_invoices", return_value=0),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", return_value=0),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
            mock.patch.object(sync_e15.asyncio, "gather", side_effect=_fake_gather),
        ):
            await sync_e15.run_daemon(settings)

    async def test_run_daemon_esali_fetches_and_decrypts_collector_config(self) -> None:
        key = sync_e15.Fernet.generate_key()
        token = sync_e15.Fernet(key).encrypt(b"pw").decode("utf-8")
        os.environ["ESALI_FERNET_KEY"] = key.decode("utf-8")

        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="esali",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url="https://x/api/",
            esali_api_key="k2",
            esali_timeout_s=60.0,
            esali_payment_method_id="6",
            esali_note="",
        )

        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                self.kwargs = _kwargs

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_invoice_more_services(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
                return {"InvoiceNo": "INV-1"}

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        async def _fake_gather(*aws: Any) -> None:
            # Actually run the loops once (sleep sets stop_event).
            for aw in aws:
                try:
                    await aw
                except Exception:
                    pass
            return None

        async def _fake_generate(
            smrc: Any, http_client: Any, e15: Any, store: Any, limit: int, concurrency: int, **_kwargs: Any
        ) -> int:
            # Trigger config fetch/decrypt by creating one invoice.
            r = await e15.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1,
                    miner_name="n",
                    phone="0123456789",
                    total_amount=1,
                    market_name="m",
                    collector_username="collector1",
                )
            )
            self.assertEqual(r.invoice_id, "INV-1")
            return 1

        async def _fake_get_cfg(self_smrc: Any, _http: Any, collector_username: str) -> dict[str, Any]:
            self.assertEqual(collector_username, "collector1")
            return {
                "collector_username": "collector1",
                "esali_username": "u",
                "esali_password_enc": token,
                "esali_service_id": "S1",
            }

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", return_value=0),
            mock.patch.object(sync_e15, "step_generate_invoices", new=_fake_generate),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", return_value=0),
            mock.patch.object(sync_e15.SmrcClient, "get_collector_esali_config", new=_fake_get_cfg),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
            mock.patch.object(sync_e15.asyncio, "gather", side_effect=_fake_gather),
        ):
            await sync_e15.run_daemon(settings)

    async def test_run_daemon_esali_missing_service_id_derives_and_persists(self) -> None:
        key = sync_e15.Fernet.generate_key()
        token = sync_e15.Fernet(key).encrypt(b"pw").decode("utf-8")
        os.environ["ESALI_FERNET_KEY"] = key.decode("utf-8")

        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="esali",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url="https://x/api/",
            esali_api_key="k2",
            esali_timeout_s=60.0,
            esali_payment_method_id="6",
            esali_note="",
        )

        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                self.kwargs = _kwargs

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_services(self, center_id: str) -> list[dict[str, Any]]:
                if center_id != "CID-1":
                    raise AssertionError(f"unexpected center_id {center_id!r}")
                return [{"ServiceId": "SVC-1"}]

            def get_invoice_more_services(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
                return {"InvoiceNo": "INV-1"}

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()
        seen_update: dict[str, Any] = {}
        seen_calls: dict[str, int] = {"generate": 0, "get_cfg": 0, "update": 0}
        seen_errors: list[str] = []

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        async def _fake_gather(*aws: Any) -> None:
            # Actually run the loops once (sleep sets stop_event).
            for aw in aws:
                try:
                    await aw
                except Exception as exc:
                    seen_errors.append(repr(exc))
            return None

        async def _fake_generate(
            smrc: Any, http_client: Any, e15: Any, store: Any, limit: int, concurrency: int, **_kwargs: Any
        ) -> int:
            seen_calls["generate"] += 1
            r = await e15.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1,
                    miner_name="n",
                    phone="0123456789",
                    total_amount=1,
                    market_name="m",
                    collector_username="collector1",
                )
            )
            self.assertEqual(r.invoice_id, "INV-1")
            return 1

        async def _fake_get_cfg(self_smrc: Any, _http: Any, collector_username: str) -> dict[str, Any]:
            seen_calls["get_cfg"] += 1
            self.assertEqual(collector_username, "collector1")
            return {
                "collector_username": "collector1",
                "esali_username": "u",
                "esali_password_enc": token,
                "esali_service_id": "",
            }

        async def _fake_update(self_smrc: Any, _http: Any, payload: dict[str, Any]) -> dict[str, Any]:
            seen_calls["update"] += 1
            seen_update.update(payload)
            return payload

        async def _direct_request(fn: Any, *, attempts: int = 3) -> Any:
            return await fn()

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "_request_with_retries", new=_direct_request),
            mock.patch.object(sync_e15, "step_queue_invoices", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_generate_invoices", new=_fake_generate),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15.SmrcClient, "get_collector_esali_config", new=_fake_get_cfg),
            mock.patch.object(sync_e15.SmrcClient, "update_esali_service_id", new=_fake_update),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
            mock.patch.object(sync_e15.asyncio, "gather", side_effect=_fake_gather),
        ):
            await sync_e15.run_daemon(settings)

        self.assertGreaterEqual(seen_calls["generate"], 1)
        self.assertGreaterEqual(seen_calls["get_cfg"], 1)
        self.assertEqual(seen_errors, [])
        self.assertEqual(seen_update, {"collector_username": "collector1", "esali_service_id": "SVC-1"})

    async def test_run_daemon_esali_missing_service_id_no_services_raises(self) -> None:
        key = sync_e15.Fernet.generate_key()
        token = sync_e15.Fernet(key).encrypt(b"pw").decode("utf-8")
        os.environ["ESALI_FERNET_KEY"] = key.decode("utf-8")

        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="esali",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url="https://x/api/",
            esali_api_key="k2",
            esali_timeout_s=60.0,
            esali_payment_method_id="6",
            esali_note="",
        )

        class _FakeEsaliAPI:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            def login_user(self) -> dict[str, Any]:
                return {"CenterId": "CID-1"}

            def get_services(self, center_id: str) -> list[dict[str, Any]]:
                return []

            def get_invoice_more_services(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
                return {"InvoiceNo": "INV-1"}

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        async def _fake_get_cfg(self_smrc: Any, _http: Any, collector_username: str) -> dict[str, Any]:
            return {
                "collector_username": collector_username,
                "esali_username": "u",
                "esali_password_enc": token,
                "esali_service_id": "",
            }

        async def _fake_generate(
            smrc: Any, http_client: Any, e15: Any, store: Any, limit: int, concurrency: int, **_kwargs: Any
        ) -> int:
            await e15.create_invoice(
                sync_e15.QueuedInvoice(
                    id=1,
                    miner_name="n",
                    phone="0123456789",
                    total_amount=1,
                    market_name="m",
                    collector_username="collector1",
                )
            )
            return 1

        with (
            mock.patch.object(sync_e15, "EsaliAPI", _FakeEsaliAPI),
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", return_value=0),
            mock.patch.object(sync_e15, "step_generate_invoices", new=_fake_generate),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", return_value=0),
            mock.patch.object(sync_e15.SmrcClient, "get_collector_esali_config", new=_fake_get_cfg),
            mock.patch.object(sync_e15.SmrcClient, "update_esali_service_id", side_effect=AssertionError("should not persist")),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
        ):
            with self.assertRaises(KeyError):
                await sync_e15.run_daemon(settings)

    async def test_sqlite_store_roundtrip_and_steps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()

            # Seed queued records via upsert_queued
            store.upsert_queued(
                [
                    sync_e15.QueuedInvoice(id=1, miner_name="a", phone="0", total_amount=1, market_name="m", collector_username="c"),
                    sync_e15.QueuedInvoice(id=2, miner_name="b", phone="0", total_amount=2, market_name="m", collector_username="c"),
                ]
            )
            self.assertEqual([x.id for x in store.get_without_invoice(10)], [1, 2])

            fake_http = _FakeAsyncClient()
            # queue_invoices endpoint response (used by step_queue_invoices)
            fake_http.enqueue(
                _FakeResponse(
                    status_code=200,
                    _json={"results": [{"id": 3, "miner_name": "c", "phone": "0", "total_amount": 3, "market_name": "m", "collector_username": "c"}]},
                )
            )
            # set_pending_payment response (used by step_generate_invoices)
            fake_http.enqueue(_FakeResponse(status_code=200, _json={"requested": 2, "updated": 2, "skipped": 0}))

            smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
            e15 = sync_e15.MockE15Client()

            # step_queue_invoices should persist id=3
            queued_saved = await sync_e15.step_queue_invoices(smrc, fake_http, store, limit=10)  # type: ignore[arg-type]
            self.assertEqual(queued_saved, 1)

            # step_generate_invoices should create invoice_ids for existing QUEUED rows and call set_pending_payment
            generated = await sync_e15.step_generate_invoices(
                smrc, fake_http, e15, store, limit=10, concurrency=5, mark_paid_first_check_delay_s=0.0  # type: ignore[arg-type]
            )
            self.assertGreaterEqual(generated, 1)

            # Now mark paid step uses external check + mark_paid API
            fake_http.enqueue(_FakeResponse(status_code=200, _json={"requested": 1, "updated": 1, "skipped": 0}))
            paid = await sync_e15.step_mark_paid(smrc, fake_http, e15, store, limit=10, concurrency=5)  # type: ignore[arg-type]
            self.assertGreaterEqual(paid, 0)

    async def test_sqlite_store_state_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()

            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=10, miner_name="m", phone="0", total_amount=5, market_name="x", collector_username="c")]
            )
            self.assertEqual([x.id for x in store.get_without_invoice(10)], [10])

            store.set_invoice_generated([sync_e15.E15Result(id=10, invoice_id="inv10")], first_check_delay_s=0.0)
            store.mark_pending_payment_sent([10])
            self.assertEqual(store.get_without_invoice(10), [])

            now_ms = int(time.time() * 1000)
            unpaid = store.get_unpaid_with_invoice(10, now_ms)
            self.assertEqual(unpaid, [(10, "inv10", "c")])

            store.delete_invoices_after_smrc_mark_paid([10])
            self.assertEqual(store.get_unpaid_with_invoice(10, now_ms), [])

            # also accept rrn tuple
            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=11, miner_name="m", phone="0", total_amount=5, market_name="x", collector_username="c")]
            )
            store.set_invoice_generated([sync_e15.E15Result(id=11, invoice_id="inv11")], first_check_delay_s=0.0)
            store.mark_pending_payment_sent([11])
            store.delete_invoices_after_smrc_mark_paid([11])
            self.assertEqual(store.get_unpaid_with_invoice(10, now_ms), [])

    async def test_run_parallel_check_paid_filters_only_paid(self) -> None:
        class _E15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

            async def check_paid(self, invoice_id: str) -> tuple[bool, str | None]:
                if invoice_id == "inv-1":
                    return True, "r1"
                return False, None

        out = await sync_e15._run_parallel_check_paid(_E15(), [(1, "inv-1", "m"), (2, "inv-2", "m")], concurrency=2)
        self.assertEqual([(cid, (r.receipt_number if r else None)) for cid, r in out], [(1, "r1"), (2, None)])

    async def test_run_parallel_check_paid_handles_exceptions(self) -> None:
        class _E15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

            async def check_paid(self, invoice_id: str) -> tuple[bool, str | None]:
                raise RuntimeError("fail")

        out = await sync_e15._run_parallel_check_paid(_E15(), [(1, "inv-1", "m")], concurrency=1)
        self.assertEqual(out, [(1, None)])

    async def test_run_parallel_check_paid_logs_exception_for_non_runtimeerror(self) -> None:
        class _E15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

            async def check_paid(self, invoice_id: str) -> tuple[bool, str | None]:
                raise ValueError("bad")

        out = await sync_e15._run_parallel_check_paid(_E15(), [(1, "inv-1", "m")], concurrency=1)
        self.assertEqual(out, [(1, None)])

    async def test_run_parallel_check_paid_accepts_two_tuple_from_check_paid_for_collector(self) -> None:
        class _E15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

            async def check_paid_for_collector(self, invoice_id: str, collector_username: str) -> tuple[bool, str | None]:
                if collector_username != "collector1":
                    raise AssertionError(f"unexpected collector_username {collector_username!r}")
                return True, "r1"

        out = await sync_e15._run_parallel_check_paid(_E15(), [(1, "inv-1", "collector1")], concurrency=1)
        self.assertEqual([(cid, r.receipt_number if r else None) for cid, r in out], [(1, "r1")])

    async def test_run_parallel_check_paid_accepts_three_tuple_from_check_paid_for_collector(self) -> None:
        class _E15(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                return sync_e15.E15Result(id=item.id, invoice_id=f"inv-{item.id}")

            async def check_paid_for_collector(
                self, invoice_id: str, collector_username: str
            ) -> tuple[bool, str | None, str | None]:
                return True, "r1", "RRN1"

        out = await sync_e15._run_parallel_check_paid(_E15(), [(1, "inv-1", "collector1")], concurrency=1)
        self.assertEqual(len(out), 1)
        cid, r = out[0]
        self.assertEqual(cid, 1)
        self.assertIsNotNone(r)
        assert r is not None
        self.assertEqual((r.receipt_number, r.rrn_number), ("r1", "RRN1"))

    async def test_parallel_create_invoices_logs_exception_for_unexpected_errors(self) -> None:
        class _Boom(sync_e15.E15Client):
            async def create_invoice(self, item: sync_e15.QueuedInvoice) -> sync_e15.E15Result:
                raise ValueError("boom")

            async def check_paid(self, invoice_id: str) -> tuple[bool, str | None]:
                return False, None

        out = await sync_e15._run_parallel_create_invoices(
            _Boom(),
            [sync_e15.QueuedInvoice(id=1, miner_name="a", phone="", total_amount=1, market_name="m", collector_username="c")],
            concurrency=1,
        )
        self.assertEqual(out, [])

    def test_jittered_sleep(self) -> None:
        self.assertEqual(sync_e15._jittered_sleep_s(60.0, 0.0), 60.0)
        with mock.patch.object(sync_e15.random, "uniform", return_value=6.0):
            self.assertEqual(sync_e15._jittered_sleep_s(60.0, 0.1), 66.0)

    def test_get_unpaid_respects_first_check_delay_and_next_at(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "t.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=7, miner_name="m", phone="0", total_amount=1, market_name="x", collector_username="c")]
            )
            store.set_invoice_generated([sync_e15.E15Result(id=7, invoice_id="inv7")], first_check_delay_s=3600.0)
            conn = sqlite3.connect(db_path)
            try:
                next_at = int(conn.execute("SELECT paid_check_next_at_ms FROM e15_sync_invoices WHERE collection_id=7").fetchone()[0])
            finally:
                conn.close()
            self.assertEqual(store.get_unpaid_with_invoice(10, next_at - 1), [])
            self.assertEqual(store.get_unpaid_with_invoice(10, next_at), [(7, "inv7", "c")])

    def test_mark_paid_idle_sleep_s(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "t2.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            self.assertEqual(store.mark_paid_idle_sleep_s(1_000_000, 60.0), 60.0)
            store.upsert_queued(
                [sync_e15.QueuedInvoice(id=8, miner_name="m", phone="0", total_amount=1, market_name="x", collector_username="c")]
            )
            store.set_invoice_generated([sync_e15.E15Result(id=8, invoice_id="inv8")], first_check_delay_s=0.0)
            store.mark_pending_payment_sent([8])
            self.assertEqual(store.mark_paid_idle_sleep_s(int(time.time() * 1000), 60.0), 1.0)
            store.bump_paid_check_backoff([8], int(time.time() * 1000), max_delay_s=3600.0)
            conn = sqlite3.connect(db_path)
            try:
                next_at = int(conn.execute("SELECT paid_check_next_at_ms FROM e15_sync_invoices WHERE collection_id=8").fetchone()[0])
            finally:
                conn.close()
            now_ms = next_at - 500
            s = store.mark_paid_idle_sleep_s(now_ms, 60.0)
            self.assertLessEqual(s, 60.0)
            self.assertGreaterEqual(s, 0.2)

    async def test_step_consume_check_now_resets_paid_check_schedule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "reset_cn.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            store.upsert_queued(
                [
                    sync_e15.QueuedInvoice(
                        id=99, miner_name="m", phone="0123456789", total_amount=1, market_name="x", collector_username="c"
                    )
                ]
            )
            store.set_invoice_generated([sync_e15.E15Result(id=99, invoice_id="inv99")], first_check_delay_s=3600.0)
            self.assertEqual(store.get_unpaid_with_invoice(10, int(time.time() * 1000)), [])
            smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
            fake_http = _FakeAsyncClient()
            with mock.patch.object(smrc, "consume_pending_payment_check_now", mock.AsyncMock(return_value=[99])):
                n = await sync_e15.step_consume_check_now(smrc, fake_http, store)
            self.assertEqual(n, 1)
            self.assertEqual(
                store.get_unpaid_with_invoice(10, int(time.time() * 1000)),
                [(99, "inv99", "c")],
            )

    async def test_run_daemon_runs_both_loops_once(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="mock",
            external_base_url=None,
            enable_mark_paid=True,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        with (
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", return_value=1),
            mock.patch.object(sync_e15, "step_generate_invoices", return_value=2),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", return_value=3),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
        ):
            await sync_e15.run_daemon(settings)

    async def test_run_daemon_executes_mark_paid_loop_body(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="mock",
            external_base_url=None,
            enable_mark_paid=True,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()
        sleep_calls: list[float] = []

        async def _fake_sleep(s: float) -> None:
            sleep_calls.append(s)
            evt.set()
            return None

        with (
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", return_value=1),
            mock.patch.object(sync_e15, "step_generate_invoices", return_value=2),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", return_value=3),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
        ):
            await sync_e15.run_daemon(settings)

        self.assertTrue(sleep_calls)

    async def test_run_daemon_loops_handle_exceptions(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="mock",
            external_base_url=None,
            enable_mark_paid=True,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )

        class _Evt:
            def __init__(self) -> None:
                self._set = False

            def is_set(self) -> bool:
                return self._set

            def set(self) -> None:
                self._set = True

        evt = _Evt()

        async def _fake_sleep(_s: float) -> None:
            evt.set()
            return None

        with (
            mock.patch.object(sync_e15.asyncio, "Event", return_value=evt),
            mock.patch.object(sync_e15.asyncio, "sleep", side_effect=_fake_sleep),
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15, "step_queue_invoices", side_effect=httpx.TransportError("x")),
            mock.patch.object(sync_e15, "step_generate_invoices", return_value=0),
            mock.patch.object(sync_e15, "step_consume_check_now", new=mock.AsyncMock(return_value=0)),
            mock.patch.object(sync_e15, "step_mark_paid", side_effect=httpx.TransportError("y")),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
        ):
            await sync_e15.run_daemon(settings)

    async def test_step_early_return_branches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "sync.sqlite3")
            store = sync_e15.SQLiteStore(db_path)
            store.init_db()
            smrc = sync_e15.SmrcClient("http://example.com", "k", timeout_s=1.0)
            e15 = sync_e15.MockE15Client()
            fake_http = _FakeAsyncClient()

            # queue step returns 0 when no results
            fake_http.enqueue(_FakeResponse(status_code=200, _json={"results": []}))
            self.assertEqual(await sync_e15.step_queue_invoices(smrc, fake_http, store, 10), 0)  # type: ignore[arg-type]

            # generate step returns 0 when no pending
            self.assertEqual(
                await sync_e15.step_generate_invoices(smrc, fake_http, e15, store, limit=10, concurrency=2), 0  # type: ignore[arg-type]
            )

            # mark_paid step returns 0 when nothing unpaid
            self.assertEqual(
                await sync_e15.step_mark_paid(smrc, fake_http, e15, store, limit=10, concurrency=2), 0  # type: ignore[arg-type]
            )

            # SQLite early-return branches
            self.assertEqual(store.upsert_queued([]), 0)
            store.set_invoice_generated([])
            store.mark_pending_payment_sent([])
            store.delete_invoices_after_smrc_mark_paid([])

    async def test_run_daemon_signal_fallback_wires_up_and_starts_tasks(self) -> None:
        settings = sync_e15.Settings(
            base_url="http://example.com/",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="mock",
            external_base_url=None,
            enable_mark_paid=True,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )

        class _FakeLoop:
            def add_signal_handler(self, _sig: Any, _cb: Any) -> None:
                raise NotImplementedError

        async def _fake_gather(*aws: Any) -> None:
            # close passed coroutines to avoid "never awaited" warnings
            for aw in aws:
                try:
                    aw.close()
                except Exception:
                    pass
            return None

        with (
            mock.patch.object(sync_e15.asyncio, "to_thread", side_effect=lambda fn, *a: fn(*a)),
            mock.patch.object(sync_e15.asyncio, "get_running_loop", return_value=_FakeLoop()),
            mock.patch.object(sync_e15.signal, "signal"),
            mock.patch.object(sync_e15.httpx, "AsyncClient", return_value=_FakeAsyncClientCM(_FakeAsyncClient())),
            mock.patch.object(sync_e15.asyncio, "gather", side_effect=_fake_gather),
        ):
            await sync_e15.run_daemon(settings)

    def test_configure_logging_and_main(self) -> None:
        # cover _configure_logging and main wiring without starting the daemon
        os.environ["SMRC_API_KEY"] = "k"
        fake_settings = sync_e15.Settings(
            base_url="http://example.com",
            api_key="k",
            limit=1,
            concurrency=1,
            idle_sleep_s=0.1,
            timeout_s=1.0,
            db_path=":memory:",
            mark_paid_sleep_s=60.0,
            mark_paid_jitter_pct=0.1,
            mark_paid_first_check_delay_s=60.0,
            mark_paid_check_max_delay_s=3600.0,
            external_mode="mock",
            external_base_url=None,
            enable_mark_paid=False,
            esali_base_url=None,
            esali_api_key=None,
            esali_timeout_s=60.0,
            esali_payment_method_id=None,
            esali_note="",
        )

        def _fake_asyncio_run(coro: Any) -> None:
            # Ensure the coroutine is properly finalized to avoid RuntimeWarning.
            coro.close()

        with (
            mock.patch.object(sync_e15, "_parse_args", return_value=fake_settings),
            mock.patch.object(sync_e15, "_configure_logging"),
            mock.patch.object(sync_e15.asyncio, "run", side_effect=_fake_asyncio_run) as arun,
        ):
            sync_e15.main()
            arun.assert_called()

        sync_e15._configure_logging()

    def test_module_main_block_runs(self) -> None:
        # Execute module as __main__ to cover the bottom `if __name__ == "__main__": main()`.
        old_argv = list(os.sys.argv)
        old_env = dict(os.environ)
        try:
            os.environ["SMRC_API_KEY"] = "k"
            os.sys.argv = ["sync_e15"]

            def _fake_asyncio_run(coro: Any) -> None:
                coro.close()

            with (
                mock.patch("asyncio.run", side_effect=_fake_asyncio_run),
            ):
                runpy.run_module("form15_tra.cli.sync_e15", run_name="__main__")
        finally:
            os.sys.argv = old_argv
            os.environ.clear()
            os.environ.update(old_env)


class EsaliApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_esali_api_init_missing_env_raises(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                esali_api_mod.EsaliAPI()

    def test_esali_api_post_json_string_code_00_normalizes_success(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return "00"

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            out = api._post("X", {"a": 1})
            self.assertEqual(out["Response_Code"], "00")

    def test_esali_api_post_json_string_code_non_00_raises(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return "01"

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "01")

    def test_esali_api_post_json_string_invoice_id_normalizes(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return "INV-123"

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            out = api._post("X", {"a": 1})
            self.assertEqual(out["InvoiceNo"], "INV-123")

    def test_esali_api_post_list_response_code_non_00_raises(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return [{"Response_Code": "06", "Response_Description": "Internal Error"}]

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "06")

    def test_esali_api_post_dict_response_code_non_00_raises(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return {"Response_Code": "02", "Response_Description": "Authentication Error In Key"}

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "02")

    def test_esali_api_post_timeout_raises_esali_api_error_06(self) -> None:
        session = mock.Mock()
        session.post.side_effect = esali_api_mod.requests.exceptions.Timeout()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "06")

    def test_esali_api_post_invalid_json_raises_esali_api_error_06(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                raise ValueError("bad-json")

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "06")

    def test_esali_api_post_request_exception_raises_esali_api_error_06(self) -> None:
        session = mock.Mock()
        session.post.side_effect = esali_api_mod.requests.exceptions.RequestException("nope")

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "06")

    def test_esali_api_post_unexpected_response_type_raises_esali_api_error_06(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return 123

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            with self.assertRaises(esali_api_mod.EsaliAPIError) as ctx:
                api._post("X", {"a": 1})
            self.assertEqual(ctx.exception.code, "06")

    def test_esali_api_post_list_response_code_00_returns_list(self) -> None:
        class _Resp:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> Any:
                return [{"Response_Code": "00"}]

        session = mock.Mock()
        session.post.return_value = _Resp()

        with (
            mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True),
            mock.patch.object(esali_api_mod.requests, "Session", return_value=session),
        ):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")
            out = api._post("X", {"a": 1})
            self.assertIsInstance(out, list)

    def test_esali_api_wrapper_methods_call_expected_endpoints(self) -> None:
        with mock.patch.dict(os.environ, {"ESALI_USERNAME": "u", "ESALI_PASSWORD": "p", "ESALI_API_KEY": "k"}, clear=True):
            api = esali_api_mod.EsaliAPI(base_url="https://x/")

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.login_user(), {"ok": True})
            p.assert_called_with("APILoginUser", {"UserName": "u", "Password": "p", "Key": "k"})

        with mock.patch.object(api, "_post", return_value=[{"ok": True}]) as p:
            self.assertEqual(api.get_services("CID"), [{"ok": True}])
            p.assert_called_with("GetServices", {"CenterId": "CID", "key": "k"})

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.get_services_detail("CID", "SID", "PM"), {"ok": True})
            p.assert_called_with("GetServicesDetail", {"CenterId": "CID", "serviceId": "SID", "Paymentmethodid": "PM", "Key": "k"})

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.get_invoice("SID", "C", "0123456789"), {"ok": True})
            p.assert_called_with(
                "GetInvoice",
                {"UserName": "u", "Password": "p", "ServiceId": "SID", "CustomerName": "C", "Phone": "0123456789", "Key": "k"},
            )

        with self.assertRaises(ValueError):
            api.get_invoice("SID", "C", "123")

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.get_invoice_more_services([{"ServiceId": "S", "Amount": 1}], "C", "CID", "PM", "0123456789", 1.0, "n"), {"ok": True})
            p.assert_called()

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.get_receipt("INV"), {"ok": True})
            p.assert_called_with("GetReceipt", {"Username": "u", "Password": "p", "InvoiceNumber": "INV", "Key": "k"})

        with mock.patch.object(api, "_post", return_value={"ok": True}) as p:
            self.assertEqual(api.verify_receipt("R"), {"ok": True})
            p.assert_called_with("VerifyReceipt", {"Username": "u", "Password": "p", "Receiptno": "R", "Key": "k"})


if __name__ == "__main__":
    unittest.main()

