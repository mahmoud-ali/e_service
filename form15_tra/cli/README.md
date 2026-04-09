## Overview

This directory contains the E15 sync worker (`sync_e15.py`) and its runtime config (`.env`).
On production, only the contents of this folder are deployed.

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

## Configure environment

Create/edit:

- `/home/mahmoud/esali_sync/.env`

Keep permissions tight because it contains secrets:

- owner: `mahmoud`
- mode: `0600`

## Install the systemd service

The unit file is stored beside the script as:

- `/home/mahmoud/esali_sync/sync_e15.service`

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

## Important note about imports (deploying only `cli/`)

`sync_e15.py` currently imports modules using the package path `form15_tra.cli.*`.
If production truly contains only this folder (no `form15_tra` package root), the worker must be made standalone (e.g. import from `lib.*`) or you must deploy a minimal package wrapper (`form15_tra/__init__.py` + `form15_tra/cli/...`).

