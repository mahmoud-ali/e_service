## Overview

This directory contains the Form15 TRA E15 sync worker (`sync_e15.py`) plus its standalone runtime dependencies (`lib/`), systemd unit (`sync_e15.service`), and runtime config (`.env`).

The worker is a long-running daemon that:

- Pulls a batch of queued invoices from the local e_service API.
- Generates external E15 invoices in parallel (either `mock` or `esali`).
- Writes its own minimal local state to SQLite (`sync_e15.sqlite3`) to support retries/backoff.
- Bulk-updates local e_service invoice state (`set-pending-payment`, `mark-paid`).
- Optionally runs a paid-check loop (backoff + jitter), plus cancel-expired handling.

On production, only the contents of this folder are deployed.

## How it works (high level)

The daemon runs two async loops concurrently:

- **Queue & generate loop**
  - Calls the local queue endpoint to fetch up to `LIMIT` items.
  - Stores/updates items in the local SQLite state store.
  - Generates external invoices (fan-out with `CONCURRENCY`), then calls local `set-pending-payment`.
- **Mark-paid loop** (only when enabled)
  - When `--enable-mark-paid` or `ENABLE_MARK_PAID=1` is set, periodically checks unpaid invoices.
  - Uses exponential backoff (capped) with jitter between unpaid checks, stored in SQLite.
  - Supports “check-now” resets via a local endpoint (useful for operators to force immediate re-check).
  - Handles **cancel-expired**: invoices older than `CANCEL_AFTER_DAYS` since generation are checked (paid-first), otherwise cancelled via local API.

## Local e_service endpoints used

The worker calls these local endpoints (base: `SMRC_BASE_URL`):

- `POST /app/api/v1/invoice/tra/collections/queue-invoices/?limit=N`
- `POST /app/api/v1/invoice/tra/collections/set-pending-payment/`
- `POST /app/api/v1/invoice/tra/collections/mark-paid/`
- `POST /app/api/v1/invoice/tra/collections/consume-pending-payment-check-now/`
- `POST /app/api/v1/invoice/tra/collections/cancel-expired/`
- `POST /app/api/v1/invoice/tra/collections/collector-esali-config/` (per-collector Esali credentials/config)
- `POST /app/api/v1/invoice/tra/collections/update-esali-service-id/` (per-collector service id update)

Auth to local e_service API is via:

- **Header**: `X-API-KEY: <SMRC_API_KEY>`

## Run

### Development (package import)

From repo root:

```bash
python -m form15_tra.cli.sync_e15
```

### Production (standalone folder)

The script is also designed to run when only this folder is deployed (it adds its own directory to `sys.path` so `lib/*` imports work):

```bash
/home/mahmoud/esali_sync/.venv/bin/python /home/mahmoud/esali_sync/sync_e15.py
```

## Run modes (`E15_MODE` / `--external-mode`)

- **`mock`** (default): generates deterministic mock invoice IDs and simulates “paid” sometimes. Useful for smoke tests without external dependencies.
- **`esali`**: integrates with Esali; requires additional secrets/config (see below).

If `E15_MODE` is anything else, the worker exits with an error.

## Esali mode details (per-collector credentials)

When `E15_MODE=esali`, invoice generation and paid checks run **per collector**:

- The queue items must include `collector_username`.
- For each `collector_username`, the worker fetches Esali credentials/config from the local endpoint `collector-esali-config/`.
- The endpoint is expected to return (at minimum):
  - `esali_username`
  - `esali_password_enc` (encrypted; decrypted using `ESALI_FERNET_KEY`)
  - `esali_service_id` (Esali service id used for invoice generation)
- If `esali_service_id` is missing, the worker attempts to determine it and then calls `update-esali-service-id/` to persist it for that collector.

Note: if a queue item phone is missing/empty, the worker falls back to `0123456789` for Esali invoice generation.

## Configuration

Configuration can be provided by **environment variables** and/or **CLI flags**. CLI flags default to env var values (and then to built-in defaults).

When running `sync_e15.py`, it will also try to load a `.env` file located beside the script (best-effort), so you can run it without exporting variables in your shell.

### CLI flags

The script supports these flags (all optional unless noted):

- **`--base-url`**: local e_service base URL  
  - env: `SMRC_BASE_URL`  
  - default: `http://127.0.0.1:8000`
- **`--api-key`**: local e_service API key (**required**)  
  - env: `SMRC_API_KEY`  
  - default: empty → exits if missing
- **`--limit`**: batch size  
  - env: `LIMIT`  
  - default: `50` (clamped to `1..500`)
- **`--concurrency`**: parallelism for external calls  
  - env: `CONCURRENCY`  
  - default: `20`
- **`--idle-sleep-s`**: sleep between queue/generate iterations  
  - env: `IDLE_SLEEP_S`  
  - default: `3.0`
- **`--timeout-s`**: timeout (seconds) for local e_service HTTP calls  
  - env: `TIMEOUT_S`  
  - default: `20.0`
- **`--db-path`**: path to the daemon’s SQLite state DB  
  - env: `DB_PATH`  
  - default: `form15_tra/cli/sync_e15.sqlite3`
- **`--external-mode`**: which external integration to use  
  - env: `E15_MODE`  
  - default: `mock` (supported: `mock`, `esali`)
- **`--external-base-url`**: reserved for later (currently unused by the worker logic)  
  - env: `E15_BASE_URL`

Mark-paid loop:

- **`--enable-mark-paid`**: enable the mark-paid loop  
  - env: `ENABLE_MARK_PAID` (set to `1` to enable without flag)  
  - default: disabled
- **`--mark-paid-sleep-s`**: base sleep (seconds) between mark-paid cycles (before jitter)  
  - env: `MARK_PAID_SLEEP_S`  
  - default: `60.0`
- **`--mark-paid-jitter-pct`**: jitter percentage (0..1) applied to mark-paid sleep  
  - env: `MARK_PAID_JITTER_PCT`  
  - default: `0.10` (clamped to `0..1`)
- **`--mark-paid-first-check-delay-s`**: delay before first paid check per generated invoice  
  - env: `MARK_PAID_FIRST_CHECK_DELAY_S` (used if the flag is omitted)  
  - default (env fallback): `60.0`
- **`--mark-paid-check-max-delay-s`**: cap (seconds) for 2^retries paid-check backoff  
  - env: `MARK_PAID_CHECK_MAX_DELAY_S` (used if the flag is omitted)  
  - default (env fallback): `3600.0`

Cancel-expired:

- **`--cancel-after-days`**: days after invoice generation to treat unpaid invoices as expired  
  - env: `CANCEL_AFTER_DAYS`  
  - default: `3` (min `1`)

Esali mode:

- **`--esali-base-url`**: Esali base URL  
  - env: `ESALI_BASE_URL`  
  - default: `https://192.168.99.10:5050/`
- **`--esali-api-key`**: Esali API key  
  - env: `ESALI_API_KEY`  
  - default: empty (required when `E15_MODE=esali`)
- **`--esali-timeout-s`**: Esali HTTP timeout (seconds)  
  - env: `ESALI_TIMEOUT_S`  
  - default: `60.0`
- **`--esali-payment-method-id`**: Esali payment method id  
  - env: `ESALI_PAYMENT_METHOD_ID`  
  - default: empty (required when `E15_MODE=esali`)
- **`--esali-note`**: note field passed to Esali when generating invoices  
  - env: `ESALI_NOTE`  
  - default: empty

### Operational “check now” behavior (mark-paid loop)

When the mark-paid loop is enabled, the worker also calls:

- `POST /app/api/v1/invoice/tra/collections/consume-pending-payment-check-now/`

This endpoint returns a list of collection IDs that should be checked immediately (operator-triggered). The worker uses it to reset paid-check backoff scheduling in its local SQLite DB for those IDs.

### Environment variables

You can configure everything purely via env vars (recommended for production via systemd `EnvironmentFile`).

Local e_service:

- **`SMRC_BASE_URL`**: base URL for local API (`http://127.0.0.1:8000` default)
- **`SMRC_API_KEY`**: local API key (**required**)
- **`TIMEOUT_S`**: local API timeout seconds (default `20`)

Worker tuning:

- **`LIMIT`**: batch size (default `50`)
- **`CONCURRENCY`**: external fan-out concurrency (default `20`)
- **`IDLE_SLEEP_S`**: sleep seconds between queue/generate iterations (default `3`)
- **`DB_PATH`**: SQLite DB path (default `form15_tra/cli/sync_e15.sqlite3`)
- **`E15_LOG_LEVEL`**: log level (`INFO` default)

External mode selection:

- **`E15_MODE`**: `mock` (default) or `esali`
- **`E15_BASE_URL`**: reserved for later

Mark-paid loop:

- **`ENABLE_MARK_PAID`**: set to `1` to enable mark-paid loop
- **`MARK_PAID_SLEEP_S`**: base loop sleep (default `60`)
- **`MARK_PAID_JITTER_PCT`**: jitter fraction 0..1 (default `0.10`)
- **`MARK_PAID_FIRST_CHECK_DELAY_S`**: wait before first paid check (default `60`)
- **`MARK_PAID_CHECK_MAX_DELAY_S`**: cap for backoff delay (default `3600`)

Cancel-expired:

- **`CANCEL_AFTER_DAYS`**: days after generation to cancel if unpaid (default `3`)

Esali integration:

- **`ESALI_BASE_URL`**: Esali root URL (default `https://192.168.99.10:5050/`)
- **`ESALI_API_KEY`**: Esali API key (**required** when `E15_MODE=esali`)
- **`ESALI_TIMEOUT_S`**: Esali timeout seconds (default `60`)
- **`ESALI_PAYMENT_METHOD_ID`**: payment method id (**required** when `E15_MODE=esali`)
- **`ESALI_NOTE`**: optional note for invoice creation
- **`ESALI_FERNET_KEY`**: Fernet key used to decrypt per-collector Esali passwords (**required** when `E15_MODE=esali`)

## SQLite state (`sync_e15.sqlite3`)

The daemon maintains its own small SQLite database (separate from Django DB) to store sync state, retries, and scheduling. It is created automatically if missing.

The DB tracks (high level):

- collection id, invoice identifiers (invoice id, receipt number, rrn number)
- statuses + timestamps for each step
- paid-check retries and next-check scheduling (backoff)

## What gets deployed

Copy the contents of this folder to the production target directory (example used below):

- `/home/mahmoud/esali_sync/`
  - `sync_e15.py`
  - `sync_e15.service`
  - `.env`
  - `lib/`
  - `sync_e15.sqlite3` (created automatically if missing)

## Prerequisites (production server)

- Python virtualenv available at `/home/mahmoud/esali_sync/.venv/`
- The service runs as user `mahmoud` (non-root)
- Network access from this host to:
  - the local e_service API (`SMRC_BASE_URL`)
  - the external E15 provider (Esali) if `E15_MODE=esali`

## Configure environment (production)

Create/edit:

- `/home/mahmoud/esali_sync/.env`

Keep permissions tight because it contains secrets:

- owner: `mahmoud`
- mode: `0600`

Example `.env` (mock mode):

```bash
SMRC_BASE_URL=http://127.0.0.1:8000
SMRC_API_KEY=changeme

E15_MODE=mock

LIMIT=50
CONCURRENCY=20
IDLE_SLEEP_S=3
TIMEOUT_S=20

DB_PATH=/home/mahmoud/esali_sync/sync_e15.sqlite3
E15_LOG_LEVEL=INFO
```

Example `.env` (esali mode):

```bash
SMRC_BASE_URL=http://127.0.0.1:8000
SMRC_API_KEY=changeme

E15_MODE=esali
ESALI_BASE_URL=https://192.168.99.10:5050/
ESALI_API_KEY=changeme
ESALI_TIMEOUT_S=60
ESALI_PAYMENT_METHOD_ID=changeme
ESALI_NOTE=

# Required: used to decrypt per-collector Esali passwords returned by the local API.
ESALI_FERNET_KEY=changeme

# Enable paid checking + expiration handling
ENABLE_MARK_PAID=1
MARK_PAID_SLEEP_S=60
MARK_PAID_JITTER_PCT=0.10
MARK_PAID_FIRST_CHECK_DELAY_S=60
MARK_PAID_CHECK_MAX_DELAY_S=3600
CANCEL_AFTER_DAYS=3

DB_PATH=/home/mahmoud/esali_sync/sync_e15.sqlite3
E15_LOG_LEVEL=INFO
```

## Install the systemd service

The unit file is stored beside the script as:

- `/home/mahmoud/esali_sync/sync_e15.service`

It uses:

- `EnvironmentFile=/home/mahmoud/esali_sync/.env`
- `ExecStart=/home/mahmoud/esali_sync/.venv/bin/python /home/mahmoud/esali_sync/sync_e15.py`

Register it with systemd and start it:

```bash
sudo ln -sf /home/mahmoud/esali_sync/sync_e15.service /etc/systemd/system/sync_e15.service
sudo systemctl daemon-reload
sudo systemctl enable --now sync_e15.service
```

## Verify / troubleshooting

Follow logs:

```bash
journalctl -u sync_e15.service -f
```

Check status and restart count:

```bash
systemctl status sync_e15.service
```

Restart manually:

```bash
sudo systemctl restart sync_e15.service
```

Common issues:

- **Missing local API key**: if `SMRC_API_KEY` / `--api-key` is not set, the worker exits immediately.
- **Unsupported mode**: `E15_MODE` must be `mock` or `esali`.
- **Esali missing secrets**: when `E15_MODE=esali`, you must provide `ESALI_API_KEY`, `ESALI_PAYMENT_METHOD_ID`, and `ESALI_FERNET_KEY`.
- **Need more logs**: set `E15_LOG_LEVEL=DEBUG` and restart the service.
