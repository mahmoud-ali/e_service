# Plan: Add Cancelation State to Sale, MeltBatch, and Storage Models

## Context

The user wants to add a `STATE_CANCLED` state to the three secondary-operation models (`MeltBatch`, `Sale`, `Storage`), mirroring the existing cancel pattern on `AppMoveGoldTraditional`. Only users of type **JIHAT_TARHIL (2)**, **BOTH (3)**, and **STATE_MANAGER (4)** may cancel, and only while the record is in `STATE_PENDING` (i.e. before completion).

Current state machines:
- `MeltBatch`: `STATE_PENDING (1)` → `STATE_COMPLETE (2)`
- `Sale`: `STATE_PENDING (1)` → `STATE_COMPLETE (2)`
- `Storage`: `STATE_PENDING (1)` → `STATE_COMPLETE (2)`

Target state machines:
- All three: `STATE_PENDING (1)` → `STATE_COMPLETE (2)` or `STATE_CANCLED (3)`

## Approach

1. Add `STATE_CANCLED = 3` to each model's class constants and update `STATE_CHOICES`.
2. Add `clean()` guard on each model to prevent modification when canceled.
3. In each admin class:
   - Add a `cancel_view` (GET → confirmation page, POST → perform cancel).
   - Add a `cancel_button` column in `list_display`.
   - Add cancel URL to `get_urls()`.
   - Update `has_change_permission`, `get_readonly_fields`, `has_delete_permission` to treat `STATE_CANCLED` like `STATE_COMPLETE` (locked).
4. Create a new generic `cancel_confirm.html` template since the existing one references `AppMoveGoldTraditional`-specific fields. The new template will show only common fields (`code`, `get_state_display`).
5. Generate a migration.

## Files to Modify

| File | Changes |
|------|---------|
| `models.py` | Add `STATE_CANCLED` constant + update `STATE_CHOICES` + add `clean()` guard in `MeltBatch`, `Sale`, `Storage` |
| `admin/melt.py` | Add `cancel_button`, `cancel_view`, cancel URL, update permission guards |
| `admin/sales.py` | Same as above for `SaleAdmin` |
| `admin/storage.py` | Same as above for `StorageAdmin` |

## Key Design Decisions

1. **Cancel state value**: `STATE_CANCLED = 3` (after `STATE_PENDING=1`, `STATE_COMPLETE=2`).
2. **User types allowed**: `JIHAT_TARHIL (2)`, `BOTH (3)`, and `STATE_MANAGER (4)`.
3. **Allowed transitions**: Only `STATE_PENDING → STATE_CANCLED` (i.e., before completion).
4. **Locked behavior**: A canceled record is read-only everywhere, same as `STATE_COMPLETE`.
5. **Template**: Create a new generic `cancel_confirm.html` at `templates/admin/gold_travel_traditional/cancel_confirm.html` that works for any model (shows `code`, `state`, warning message).

## Steps

- [x] **Step 1**: Update `models.py` — add `STATE_CANCLED` to `MeltBatch`, `Sale`, `Storage`, update `STATE_CHOICES`, add `clean()` guards.
- [x] **Step 2**: Update `admin/melt.py` — add cancel URL, `cancel_view`, `cancel_button`, update permission/readonly guards.
- [x] **Step 3**: Update `admin/sales.py` — same as step 2.
- [x] **Step 4**: Update `admin/storage.py` — same as step 2.
- [x] **Step 5**: Create a shared cancel-confirm template (or copy to each model's template dir).
- [x] **Step 6**: Generate migration with `makemigrations`.
- [x] **Step 7**: Update `AGENTS.md` state machine diagrams.

## Verification

1. Run `python manage.py test gold_travel_traditional` to confirm existing tests still pass.
2. Manual check: create `Sale`/`MeltBatch`/`Storage` in `STATE_PENDING`, verify cancel button appears for user types 2, 3, 4, verify cancel sets state to 3, verify canceled record fields are read-only.
