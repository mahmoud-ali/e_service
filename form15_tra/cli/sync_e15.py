"""
Daemon-ish sync process for Form15 TRA invoices.

It pulls a batch from the local queue endpoint, fans out each item to another
service in parallel (async), then bulk-updates local state via the provided
bulk endpoints.

Endpoints (local e_service):
- POST {BASE_URL}/app/api/v1/invoice/tra/collections/queue-invoices/?limit=N
- POST {BASE_URL}/app/api/v1/invoice/tra/collections/set-pending-payment/
- POST {BASE_URL}/app/api/v1/invoice/tra/collections/mark-paid/

Auth:
- Header: X-API-KEY: <key>

Run:
- .venv/bin/python -m form15_tra.cli.sync_e15

Config via env (or CLI args):
- SMRC_BASE_URL (default: http://127.0.0.1:8000)
- SMRC_API_KEY (required)
- LIMIT (default: 50)
- CONCURRENCY (default: 20)
- IDLE_SLEEP_S (default: 3)
- TIMEOUT_S (default: 20)
- E15_MODE (default: mock; values: mock|esali)
- E15_BASE_URL (reserved for later)
- ESALI_BASE_URL (default: https://192.168.99.10:5050/)
- ESALI_API_KEY (required when E15_MODE=esali)
- ESALI_TIMEOUT_S (default: 60)
- ESALI_PAYMENT_METHOD_ID (required when E15_MODE=esali)
- ESALI_NOTE (optional)
- ESALI_FERNET_KEY (required when E15_MODE=esali; decrypt collector passwords)
- DB_PATH (default: form15_tra/cli/sync_e15.sqlite3)
- MARK_PAID_SLEEP_S (default: 60)
- MARK_PAID_JITTER_PCT (default: 0.10)
- ENABLE_MARK_PAID (set to \"1\" to enable)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
from pathlib import Path
import random
import signal
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Optional

import httpx
from dotenv import load_dotenv

from form15_tra.cli.lib.esali_api import EsaliAPI, EsaliAPIError
from cryptography.fernet import Fernet, InvalidToken


logger = logging.getLogger("sync_e15")

# Load `form15_tra/cli/.env` if present, so this module can be run directly
# without requiring shell export. This is intentionally best-effort.
_DEFAULT_DOTENV_PATH = Path(__file__).with_name(".env")
load_dotenv(_DEFAULT_DOTENV_PATH, override=False)

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _normalize_base_url(url: str) -> str:
    return url.rstrip("/")


def _backoff_sleep_s(attempt: int, base: float = 0.25, cap: float = 5.0) -> float:
    return min(cap, base * (2**attempt)) * (0.5 + random.random())


@dataclass(frozen=True)
class QueuedInvoice:
    id: int
    miner_name: str
    phone: str
    total_amount: Any
    market_name: str
    collector_username: str


@dataclass(frozen=True)
class E15Result:
    id: int
    invoice_id: str
    receipt_number: Optional[str] = None
    rrn_number: Optional[str] = None


class SQLiteStore:
    """
    Standalone daemon-managed SQLite state store (separate from Django DB).
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        # isolation_level=None enables autocommit, which is simplest/safest for this small daemon state DB.
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def init_db(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS e15_sync_invoices (
                    collection_id INTEGER PRIMARY KEY,
                    miner_name TEXT,
                    phone TEXT,
                    total_amount TEXT,
                    market_name TEXT,
                    collector_username TEXT,
                    status TEXT NOT NULL,
                    invoice_id TEXT NULL,
                    receipt_number TEXT NULL,
                    rrn_number TEXT NULL,
                    queued_at INTEGER,
                    invoice_generated_at INTEGER NULL,
                    pending_payment_sent_at INTEGER NULL,
                    paid_at INTEGER NULL,
                    last_error TEXT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            # Backfill schema for existing DBs created before `phone` existed.
            cols = {r[1] for r in conn.execute("PRAGMA table_info(e15_sync_invoices)").fetchall()}
            if "phone" not in cols:
                conn.execute("ALTER TABLE e15_sync_invoices ADD COLUMN phone TEXT;")
            if "rrn_number" not in cols:
                conn.execute("ALTER TABLE e15_sync_invoices ADD COLUMN rrn_number TEXT;")
            if "collector_username" not in cols:
                conn.execute("ALTER TABLE e15_sync_invoices ADD COLUMN collector_username TEXT;")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_e15_status_invoice ON e15_sync_invoices(status, invoice_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_e15_invoice_paid ON e15_sync_invoices(invoice_id, paid_at)"
            )
        finally:
            conn.close()

    def upsert_queued(self, items: list["QueuedInvoice"]) -> int:
        now = int(time.time() * 1000)
        rows = [
            (
                i.id,
                i.miner_name,
                i.phone,
                str(i.total_amount),
                i.market_name,
                i.collector_username,
                "QUEUED",
                now,
                now,
            )
            for i in items
        ]
        if not rows:
            return 0
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO e15_sync_invoices (
                    collection_id, miner_name, phone, total_amount, market_name, collector_username, status, queued_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(collection_id) DO UPDATE SET
                    miner_name=excluded.miner_name,
                    phone=excluded.phone,
                    total_amount=excluded.total_amount,
                    market_name=excluded.market_name,
                    collector_username=excluded.collector_username,
                    status=CASE
                        WHEN e15_sync_invoices.status='PAID' THEN e15_sync_invoices.status
                        ELSE excluded.status
                    END,
                    queued_at=COALESCE(e15_sync_invoices.queued_at, excluded.queued_at),
                    updated_at=excluded.updated_at
                """,
                rows,
            )
            return len(rows)
        finally:
            conn.close()

    def get_without_invoice(self, limit: int) -> list["QueuedInvoice"]:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                SELECT collection_id, miner_name, phone, total_amount, market_name, collector_username
                FROM e15_sync_invoices
                WHERE invoice_id IS NULL AND status='QUEUED'
                ORDER BY queued_at ASC, collection_id ASC
                LIMIT ?
                """,
                (limit,),
            )
            out: list[QueuedInvoice] = []
            for r in cur.fetchall():
                out.append(
                    QueuedInvoice(
                        id=int(r["collection_id"]),
                        miner_name=str(r["miner_name"] or ""),
                        phone=str(r["phone"] or ""),
                        total_amount=r["total_amount"],
                        market_name=str(r["market_name"] or ""),
                        collector_username=str(r["collector_username"] or ""),
                    )
                )
            return out
        finally:
            conn.close()

    def set_invoice_generated(self, results: list["E15Result"]) -> None:
        if not results:
            return
        now = int(time.time() * 1000)
        rows = [(r.invoice_id, now, now, "INVOICE_GENERATED", r.id) for r in results]
        conn = self._connect()
        try:
            conn.executemany(
                """
                UPDATE e15_sync_invoices
                SET invoice_id=?, invoice_generated_at=?, updated_at=?, status=?
                WHERE collection_id=?
                """,
                rows,
            )
        finally:
            conn.close()

    def mark_pending_payment_sent(self, ids: list[int]) -> None:
        if not ids:
            return
        now = int(time.time() * 1000)
        conn = self._connect()
        try:
            conn.executemany(
                """
                UPDATE e15_sync_invoices
                SET pending_payment_sent_at=?, updated_at=?, status=?
                WHERE collection_id=?
                """,
                [(now, now, "PENDING_PAYMENT_SENT", i) for i in ids],
            )
        finally:
            conn.close()

    def get_unpaid_with_invoice(self, limit: int) -> list[tuple[int, str, str]]:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                SELECT collection_id, invoice_id, collector_username
                FROM e15_sync_invoices
                WHERE invoice_id IS NOT NULL AND paid_at IS NULL
                ORDER BY invoice_generated_at ASC, collection_id ASC
                LIMIT ?
                """,
                (limit,),
            )
            return [
                (int(r["collection_id"]), str(r["invoice_id"]), str(r["collector_username"] or ""))
                for r in cur.fetchall()
            ]
        finally:
            conn.close()

    def mark_paid(self, paid: list[tuple]) -> None:
        if not paid:
            return
        now = int(time.time() * 1000)
        norm: list[tuple[int, str, Optional[str]]] = []
        for row in paid:
            if len(row) == 2:
                cid, receipt = row
                rrn = None
            else:
                cid, receipt, rrn = row[0], row[1], row[2]
            norm.append((int(cid), str(receipt), None if rrn is None else str(rrn)))
        rows = [(receipt, rrn, now, now, "PAID", cid) for (cid, receipt, rrn) in norm]
        conn = self._connect()
        try:
            conn.executemany(
                """
                UPDATE e15_sync_invoices
                SET receipt_number=?, rrn_number=?, paid_at=?, updated_at=?, status=?
                WHERE collection_id=?
                """,
                rows,
            )
        finally:
            conn.close()


class E15APIError(RuntimeError):
    pass


class SmrcClient:
    def __init__(self, base_url: str, api_key: str, timeout_s: float) -> None:
        self.base_url = _normalize_base_url(base_url)
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout_s)

    def _headers(self) -> dict[str, str]:
        return {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    async def queue_invoices(self, client: httpx.AsyncClient, limit: int) -> list[QueuedInvoice]:
        url = f"{self.base_url}/app/api/v1/invoice/tra/collections/queue-invoices/"
        resp = await client.post(url, params={"limit": limit}, headers=self._headers(), timeout=self.timeout)
        if resp.status_code != 200:
            raise E15APIError(f"queue_invoices failed: {resp.status_code} {resp.text}")
        data = resp.json()
        results = data.get("results") or []
        out: list[QueuedInvoice] = []
        for row in results:
            try:
                if not isinstance(row, dict):
                    logger.warning("Skipping malformed queue item (not an object): %r", row)
                    continue
                if "id" not in row:
                    logger.warning("Skipping malformed queue item (missing id): %s", row)
                    continue
                raw_id = row.get("id")
                if raw_id is None or str(raw_id).strip() == "":
                    logger.warning("Skipping malformed queue item (empty id): %s", row)
                    continue
                out.append(
                    QueuedInvoice(
                        id=int(raw_id),
                        miner_name=str(row.get("miner_name", "")),
                        phone=str(row.get("phone", "")),
                        total_amount=row.get("total_amount"),
                        market_name=str(row.get("market_name", "")),
                        collector_username=str(row.get("collector_username", "")),
                    )
                )
            except Exception:
                # Keep this quiet (no traceback) because malformed queue items are expected sometimes.
                logger.warning("Skipping malformed queue item: %s", row)
        return out

    async def set_pending_payment(
        self, client: httpx.AsyncClient, invoices: Iterable[E15Result]
    ) -> dict[str, Any]:
        payload = {"invoices": [{"id": r.id, "invoice_id": r.invoice_id} for r in invoices]}
        if not payload["invoices"]:
            return {"requested": 0, "updated": 0, "skipped": 0}
        url = f"{self.base_url}/app/api/v1/invoice/tra/collections/set-pending-payment/"
        resp = await client.post(url, headers=self._headers(), timeout=self.timeout, json=payload)
        if resp.status_code != 200:
            raise E15APIError(f"set_pending_payment failed: {resp.status_code} {resp.text}")
        return resp.json()

    async def mark_paid(self, client: httpx.AsyncClient, receipts: Iterable[E15Result]) -> dict[str, Any]:
        out_receipts: list[dict[str, Any]] = []
        for r in receipts:
            if r.receipt_number is None or r.receipt_number == "":
                continue
            row: dict[str, Any] = {"id": r.id, "receipt_number": r.receipt_number}
            if r.rrn_number is not None and r.rrn_number != "":
                row["rrn_number"] = r.rrn_number
            out_receipts.append(row)
        payload = {"receipts": out_receipts}
        if not payload["receipts"]:
            return {"requested": 0, "updated": 0, "skipped": 0}
        url = f"{self.base_url}/app/api/v1/invoice/tra/collections/mark-paid/"
        resp = await client.post(url, headers=self._headers(), timeout=self.timeout, json=payload)
        if resp.status_code != 200:
            raise E15APIError(f"mark_paid failed: {resp.status_code} {resp.text}")
        return resp.json()

    async def get_collector_esali_config(self, client: httpx.AsyncClient, collector_username: str) -> dict[str, Any]:
        url = f"{self.base_url}/app/api/v1/invoice/tra/collections/collector-esali-config/"
        payload = {"collector_username": collector_username}
        resp = await client.post(url, headers=self._headers(), timeout=self.timeout, json=payload)
        if resp.status_code != 200:
            raise E15APIError(f"collector_esali_config failed: {resp.status_code} {resp.text}")
        data = resp.json()
        if not isinstance(data, dict):
            raise E15APIError(f"collector_esali_config invalid response: {data!r}")
        return data

    async def update_esali_service_id(self, client: httpx.AsyncClient, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/app/api/v1/invoice/tra/collections/update-esali-service-id/"
        resp = await client.post(url, headers=self._headers(), timeout=self.timeout, json=payload)
        if resp.status_code != 200:
            raise E15APIError(f"update_esali_service_id failed: {resp.status_code} {resp.text}")
        data = resp.json()
        if not isinstance(data, dict):
            raise E15APIError(f"update_esali_service_id invalid response: {data!r}")
        return data


class E15Client:
    async def create_invoice(self, item: QueuedInvoice) -> E15Result:
        raise NotImplementedError

    async def check_paid(self, invoice_id: str) -> tuple[bool, Optional[str]]:
        raise NotImplementedError


class MockE15Client(E15Client):
    async def create_invoice(self, item: QueuedInvoice) -> E15Result:
        await asyncio.sleep(0.01)
        seed = json.dumps(
            {"id": item.id, "miner_name": item.miner_name, "total_amount": item.total_amount, "market": item.market_name},
            sort_keys=True,
            default=str,
        ).encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()[:16]
        invoice_id = f"MOCK-{item.id}-{digest}"
        return E15Result(id=item.id, invoice_id=invoice_id, receipt_number=None)

    async def check_paid(self, invoice_id: str) -> tuple[bool, Optional[str]]:
        await asyncio.sleep(0.01)
        digest = hashlib.sha256(invoice_id.encode("utf-8")).hexdigest()
        is_paid = (int(digest[:2], 16) % 4) == 0
        if not is_paid:
            return False, None
        return True, f"RCP-{digest[-10:]}"

def _require_nonempty(value: str, name: str) -> str:
    if value is None or str(value).strip() == "":
        raise SystemExit(f"{name} is required when E15_MODE=esali.")
    return str(value).strip()


def _get_fernet_from_env() -> Fernet:
    raw = os.getenv("ESALI_FERNET_KEY", "")
    raw = str(raw).strip()
    if raw == "":
        raise RuntimeError("ESALI_FERNET_KEY is required when E15_MODE=esali.")
    return Fernet(raw.encode("utf-8"))


def _decrypt_esali_password(enc: str) -> str:
    token = str(enc or "").strip()
    if token == "":
        return ""
    try:
        return _get_fernet_from_env().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Failed to decrypt esali_password_enc") from exc


def _extract_receipt_number(receipt_resp: Any) -> Optional[str]:
    """
    Esali GetReceipt response shapes vary; support dict or single-item list.
    We only need LOCALRECEIPTNO as our receipt_number.
    """
    if isinstance(receipt_resp, list):
        if not receipt_resp:
            return None
        receipt_resp = receipt_resp[0]
    if not isinstance(receipt_resp, dict):
        return None
    for k in ("LOCALRECEIPTNO", "LocalReceiptNo", "localReceiptNo", "receipt_no", "ReceiptNo"):
        v = receipt_resp.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None


def _extract_rrn_number(receipt_resp: Any) -> Optional[str]:
    """
    Esali GetReceipt response shapes vary; support dict or single-item list.
    Extract RRN using the `RRN` key only.
    """
    if isinstance(receipt_resp, list):
        if not receipt_resp:
            return None
        receipt_resp = receipt_resp[0]
    if not isinstance(receipt_resp, dict):
        return None
    v = receipt_resp.get("RRN")
    if v is None or str(v).strip() == "":
        return None
    return str(v).strip()


@dataclass(frozen=True)
class EsaliCollectorConfig:
    esali_username: str
    esali_password_plain: str
    esali_service_id: str


class EsaliClient(E15Client):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_s: float,
        payment_method_id: str,
        get_collector_config: Callable[[str], Awaitable[EsaliCollectorConfig]],
        note: str = "",
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._timeout_s = float(timeout_s)
        self._payment_method_id = payment_method_id
        self._note = note
        self._get_collector_config = get_collector_config

    def _api_for_collector(self, cfg: EsaliCollectorConfig) -> EsaliAPI:
        return EsaliAPI(
            base_url=self._base_url,
            username=cfg.esali_username,
            password=cfg.esali_password_plain,
            api_key=self._api_key,
            timeout=int(self._timeout_s),
        )

    async def _login_center_id(self, api: EsaliAPI) -> str:
        resp = await asyncio.to_thread(api.login_user)
        center_id = None
        if isinstance(resp, dict):
            center_id = resp.get("CenterId") or resp.get("CENTERID") or resp.get("centerId")
        if center_id is None or str(center_id).strip() == "":
            raise EsaliAPIError("01", "Failed to get CenterId")
        return str(center_id).strip()

    async def get_services(self, api: EsaliAPI) -> list[dict[str, Any]]:
        resp = await asyncio.to_thread(api.get_services)
        if isinstance(resp, list):
            return resp
        return []


    def _map_item(self, item: QueuedInvoice, cfg: EsaliCollectorConfig) -> tuple[list[dict[str, Any]], str, str, float]:
        customer_name = (item.miner_name or "").strip()
        phone = (item.phone or "").strip() or "0123456789"
        try:
            total_amount = float(item.total_amount or 0)
        except Exception:
            total_amount = 0.0
        services = [{"ServiceId": cfg.esali_service_id, "amount": total_amount}]
        return services, customer_name, phone, total_amount

    async def create_invoice(self, item: QueuedInvoice) -> E15Result:
        collector_username = str(item.collector_username or "").strip()
        if collector_username == "":
            raise KeyError("Missing collector_username for Esali mapping.")
        cfg = await self._get_collector_config(collector_username)
        api = self._api_for_collector(cfg)
        center_id = await self._login_center_id(api)
        services, customer_name, phone, total_amount = self._map_item(item, cfg)
        resp = await asyncio.to_thread(
            api.get_invoice_more_services,
            services,
            customer_name,
            center_id,
            self._payment_method_id,
            phone,
            total_amount,
            self._note,
        )
        invoice_no = None
        if isinstance(resp, dict):
            invoice_no = (
                resp.get("InvoiceNo")
                or resp.get("INVOICENO")
                or resp.get("invoiceNo")
                or resp.get("INVOICE_NO")
            )
        if invoice_no is None or str(invoice_no).strip() == "":
            raise EsaliAPIError("06", f"Missing InvoiceNo in response: {resp!r}")
        return E15Result(id=item.id, invoice_id=str(invoice_no).strip(), receipt_number=None)

    async def check_paid(self, invoice_id: str) -> tuple[bool, Optional[str]]:
        raise RuntimeError("Use check_paid_for_collector(invoice_id, collector_username) for Esali mode.")

    async def check_paid_for_collector(
        self, invoice_id: str, collector_username: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        cfg = await self._get_collector_config(collector_username)
        api = self._api_for_collector(cfg)
        _ = await self._login_center_id(api)
        try:
            resp = await asyncio.to_thread(api.get_receipt, invoice_id)
        except EsaliAPIError as exc:
            if getattr(exc, "code", None) == "01":
                return False, None, None
            raise
        receipt_no = _extract_receipt_number(resp)
        rrn_no = _extract_rrn_number(resp)
        if not receipt_no:
            return False, None, None
        return True, receipt_no, rrn_no


async def _run_parallel_create_invoices(
    e15: E15Client,
    items: list[QueuedInvoice],
    concurrency: int,
) -> list[E15Result]:
    sem = asyncio.Semaphore(max(1, concurrency))

    async def one(item: QueuedInvoice) -> Optional[E15Result]:
        async with sem:
            try:
                return await e15.create_invoice(item)
            except (KeyError, EsaliAPIError, RuntimeError) as exc:
                logger.warning("External invoice skipped for id=%s (%s)", item.id, exc)
                return None
            except Exception as exc:
                logger.exception("External service failed for id=%s", item.id)
                return None

    results = await asyncio.gather(*(one(i) for i in items))
    return [r for r in results if r is not None]


async def _run_parallel_check_paid(
    e15: E15Client, invoice_rows: list[tuple[int, str, str]], concurrency: int
) -> list[E15Result]:
    sem = asyncio.Semaphore(max(1, concurrency))

    async def one(row: tuple[int, str, str]) -> Optional[E15Result]:
        cid, invoice_id, collector_username = row
        async with sem:
            try:
                if hasattr(e15, "check_paid_for_collector"):
                    res = await getattr(e15, "check_paid_for_collector")(invoice_id, collector_username)
                    if isinstance(res, tuple) and len(res) == 3:
                        paid, receipt, rrn = res
                    else:
                        paid, receipt = res  # type: ignore[misc]
                        rrn = None
                else:
                    paid, receipt = await e15.check_paid(invoice_id)
                    rrn = None
                if not paid or not receipt:
                    return None
                return E15Result(id=cid, invoice_id=invoice_id, receipt_number=receipt, rrn_number=rrn)
            except (KeyError, EsaliAPIError, RuntimeError) as exc:
                logger.warning("External paid check skipped for id=%s invoice_id=%s (%s)", cid, invoice_id, exc)
                return None
            except Exception:
                logger.exception("External paid check failed for id=%s invoice_id=%s", cid, invoice_id)
                return None

    results = await asyncio.gather(*(one(r) for r in invoice_rows))
    return [r for r in results if r is not None]


async def _request_with_retries(fn, *, attempts: int = 3) -> Any:
    last_exc: Optional[BaseException] = None
    for attempt in range(attempts):
        try:
            return await fn()
        except (httpx.TimeoutException, httpx.TransportError, E15APIError) as exc:
            last_exc = exc
            sleep_s = _backoff_sleep_s(attempt)
            logger.warning("Request failed (%s/%s): %s; sleeping %.2fs", attempt + 1, attempts, exc, sleep_s)
            await asyncio.sleep(sleep_s)
    assert last_exc is not None
    raise last_exc


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    limit: int
    concurrency: int
    idle_sleep_s: float
    timeout_s: float
    db_path: str
    mark_paid_sleep_s: float
    mark_paid_jitter_pct: float
    external_mode: str
    external_base_url: Optional[str]
    enable_mark_paid: bool
    esali_base_url: Optional[str]
    esali_api_key: Optional[str]
    esali_timeout_s: float
    esali_payment_method_id: Optional[str]
    esali_note: str


def _parse_args() -> Settings:
    p = argparse.ArgumentParser(description="Sync Form15 TRA invoice queue to external service (daemon).")
    p.add_argument("--base-url", default=os.getenv("SMRC_BASE_URL", "http://127.0.0.1:8000"))
    p.add_argument("--api-key", default=os.getenv("SMRC_API_KEY", ""))
    p.add_argument("--limit", type=int, default=_env_int("LIMIT", 50))
    p.add_argument("--concurrency", type=int, default=_env_int("CONCURRENCY", 20))
    p.add_argument("--idle-sleep-s", type=float, default=_env_float("IDLE_SLEEP_S", 3.0))
    p.add_argument("--timeout-s", type=float, default=_env_float("TIMEOUT_S", 20.0))
    p.add_argument("--db-path", default=os.getenv("DB_PATH", "form15_tra/cli/sync_e15.sqlite3"))
    p.add_argument("--mark-paid-sleep-s", type=float, default=_env_float("MARK_PAID_SLEEP_S", 60.0))
    p.add_argument("--mark-paid-jitter-pct", type=float, default=_env_float("MARK_PAID_JITTER_PCT", 0.10))
    p.add_argument("--external-mode", default=os.getenv("E15_MODE", "mock"))
    p.add_argument("--external-base-url", default=os.getenv("E15_BASE_URL"))
    p.add_argument("--enable-mark-paid", action="store_true", default=os.getenv("ENABLE_MARK_PAID") == "1")
    p.add_argument("--esali-base-url", default=os.getenv("ESALI_BASE_URL", "https://192.168.99.10:5050/"))
    p.add_argument("--esali-api-key", default=os.getenv("ESALI_API_KEY", ""))
    p.add_argument("--esali-timeout-s", type=float, default=_env_float("ESALI_TIMEOUT_S", 60.0))
    p.add_argument("--esali-payment-method-id", default=os.getenv("ESALI_PAYMENT_METHOD_ID", ""))
    p.add_argument("--esali-note", default=os.getenv("ESALI_NOTE", ""))
    args = p.parse_args()

    if not args.api_key:
        raise SystemExit("SMRC_API_KEY (or --api-key) is required.")

    jitter = max(0.0, min(1.0, float(args.mark_paid_jitter_pct)))

    return Settings(
        base_url=args.base_url,
        api_key=args.api_key,
        limit=max(1, min(500, int(args.limit))),
        concurrency=max(1, int(args.concurrency)),
        idle_sleep_s=max(0.1, float(args.idle_sleep_s)),
        timeout_s=max(1.0, float(args.timeout_s)),
        db_path=str(args.db_path),
        mark_paid_sleep_s=max(1.0, float(args.mark_paid_sleep_s)),
        mark_paid_jitter_pct=jitter,
        external_mode=str(args.external_mode or "mock"),
        external_base_url=args.external_base_url,
        enable_mark_paid=bool(args.enable_mark_paid),
        esali_base_url=str(args.esali_base_url or "") or None,
        esali_api_key=str(args.esali_api_key or "") or None,
        esali_timeout_s=max(1.0, float(args.esali_timeout_s)),
        esali_payment_method_id=str(args.esali_payment_method_id or "") or None,
        esali_note=str(args.esali_note or ""),
    )


def _configure_logging() -> None:
    level = os.getenv("E15_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


async def step_queue_invoices(
    smrc: SmrcClient, http_client: httpx.AsyncClient, store: SQLiteStore, limit: int
) -> int:
    items = await _request_with_retries(lambda: smrc.queue_invoices(http_client, limit))
    if not items:
        return 0
    return await asyncio.to_thread(store.upsert_queued, items)


async def step_generate_invoices(
    smrc: SmrcClient,
    http_client: httpx.AsyncClient,
    e15: E15Client,
    store: SQLiteStore,
    limit: int,
    concurrency: int,
) -> int:
    pending = await asyncio.to_thread(store.get_without_invoice, limit)
    if not pending:
        return 0
    generated = await _run_parallel_create_invoices(e15, pending, concurrency)
    if not generated:
        return 0
    await asyncio.to_thread(store.set_invoice_generated, generated)
    await _request_with_retries(lambda: smrc.set_pending_payment(http_client, generated))
    await asyncio.to_thread(store.mark_pending_payment_sent, [r.id for r in generated])
    return len(generated)


async def step_mark_paid(
    smrc: SmrcClient,
    http_client: httpx.AsyncClient,
    e15: E15Client,
    store: SQLiteStore,
    limit: int,
    concurrency: int,
) -> int:
    invoice_rows = await asyncio.to_thread(store.get_unpaid_with_invoice, limit)
    if not invoice_rows:
        return 0
    paid_results = await _run_parallel_check_paid(e15, invoice_rows, concurrency)
    if not paid_results:
        return 0
    await _request_with_retries(lambda: smrc.mark_paid(http_client, paid_results))
    await asyncio.to_thread(
        store.mark_paid,
        [
            (r.id, r.receipt_number or "", r.rrn_number)
            for r in paid_results
            if r.receipt_number
        ],
    )
    return len(paid_results)


def _jittered_sleep_s(base_s: float, jitter_pct: float) -> float:
    if jitter_pct <= 0:
        return base_s
    span = base_s * jitter_pct
    return max(0.1, base_s + random.uniform(-span, span))


async def run_daemon(settings: Settings) -> None:  # pragma: no cover
    smrc = SmrcClient(settings.base_url, settings.api_key, timeout_s=settings.timeout_s)
    store = SQLiteStore(settings.db_path)
    await asyncio.to_thread(store.init_db)

    stop_event = asyncio.Event()

    def _stop(*_args: Any) -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            signal.signal(sig, lambda *_: _stop())

    limits = httpx.Limits(max_connections=max(10, settings.concurrency * 2), max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as http_client:
        # Cache Esali configs keyed by Esali username (requested), fetched lazily by collector_username.
        esali_by_username: dict[str, EsaliCollectorConfig] = {}
        collector_to_esali_username: dict[str, str] = {}

        async def _get_esali_config_for_collector(collector_username: str) -> EsaliCollectorConfig:
            key = str(collector_username or "").strip()
            if key == "":
                raise KeyError("collector_username is empty")

            cached_esali_username = collector_to_esali_username.get(key)
            if cached_esali_username:
                cached = esali_by_username.get(cached_esali_username)
                if cached is not None:
                    return cached

            data = await _request_with_retries(lambda: smrc.get_collector_esali_config(http_client, key))
            esali_username = str(data.get("esali_username", "")).strip()
            enc = str(data.get("esali_password_enc", "")).strip()
            plain = _decrypt_esali_password(enc)

            service_id = str(data.get("esali_service_id", "")).strip()
            if not esali_username or not enc:
                raise KeyError(f"Incomplete Esali config for collector {key!r}")

            if not service_id:
                # Derive service_id from Esali services list (pick first item).
                api = EsaliAPI(
                    base_url=_require_nonempty(settings.esali_base_url or "", "ESALI_BASE_URL"),
                    username=esali_username,
                    password=plain,
                    api_key=_require_nonempty(settings.esali_api_key or "", "ESALI_API_KEY"),
                    timeout=int(float(settings.esali_timeout_s)),
                )
                login = await asyncio.to_thread(api.login_user)
                center_id = None
                if isinstance(login, dict):
                    center_id = login.get("CenterId") or login.get("CENTERID") or login.get("centerId")
                if center_id is None or str(center_id).strip() == "":
                    raise KeyError(f"Missing CenterId from Esali login for collector {key!r}")
                services = await asyncio.to_thread(api.get_services, str(center_id).strip())
                if not services or not isinstance(services, list) or not isinstance(services[0], dict):
                    raise KeyError(f"Missing services list from Esali for collector {key!r}")
                raw_sid = services[0].get("ServiceId") or services[0].get("SERVICEID") or services[0].get("serviceId")
                if raw_sid is None or str(raw_sid).strip() == "":
                    raise KeyError(f"Missing ServiceId from Esali services[0] for collector {key!r}")
                service_id = str(raw_sid).strip()

                # Persist back to SMRC for future runs.
                payload = {"collector_username": key, "esali_service_id": service_id}
                await _request_with_retries(lambda: smrc.update_esali_service_id(http_client, payload))

            cfg = EsaliCollectorConfig(
                esali_username=esali_username,
                esali_password_plain=plain,
                esali_service_id=service_id,
            )
            esali_by_username[esali_username] = cfg
            collector_to_esali_username[key] = esali_username
            return cfg

        if settings.external_mode == "mock":
            e15: E15Client = MockE15Client()
        elif settings.external_mode == "esali":
            e15 = EsaliClient(
                base_url=_require_nonempty(settings.esali_base_url or "", "ESALI_BASE_URL"),
                api_key=_require_nonempty(settings.esali_api_key or "", "ESALI_API_KEY"),
                timeout_s=float(settings.esali_timeout_s),
                payment_method_id=_require_nonempty(settings.esali_payment_method_id or "", "ESALI_PAYMENT_METHOD_ID"),
                get_collector_config=_get_esali_config_for_collector,
                note=str(settings.esali_note or ""),
            )
        else:
            raise SystemExit(f"Unsupported E15_MODE={settings.external_mode!r} (supported: 'mock', 'esali').")

        async def queue_and_generate_loop() -> None:
            while not stop_event.is_set():
                try:
                    queued = await step_queue_invoices(smrc, http_client, store, settings.limit)
                    if queued:
                        logger.info("Saved %s queued invoice records", queued)

                    generated = await step_generate_invoices(smrc, http_client, e15, store, settings.limit, settings.concurrency)
                    if generated:
                        logger.info("Generated %s invoices and sent set_pending_payment", generated)
                except (httpx.TimeoutException, httpx.TransportError, E15APIError) as exc:
                    logger.warning("queue/generate loop error: %s", exc)
                await asyncio.sleep(settings.idle_sleep_s)

        async def mark_paid_loop() -> None:
            while not stop_event.is_set():
                try:
                    if settings.enable_mark_paid:
                        updated = await step_mark_paid(
                            smrc, http_client, e15, store, settings.limit, settings.concurrency
                        )
                        if updated:
                            logger.info("Marked %s invoices paid", updated)
                except (httpx.TimeoutException, httpx.TransportError, E15APIError) as exc:
                    logger.warning("mark_paid loop error: %s", exc)
                await asyncio.sleep(_jittered_sleep_s(settings.mark_paid_sleep_s, settings.mark_paid_jitter_pct))

        await asyncio.gather(queue_and_generate_loop(), mark_paid_loop())


def main() -> None:  # pragma: no cover
    _configure_logging()
    settings = _parse_args()
    asyncio.run(run_daemon(settings))


if __name__ == "__main__":
    main()

