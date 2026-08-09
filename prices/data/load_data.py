import csv
import os
import sys
import django

# Add the project root to sys.path
# Script is in gold_travel_traditional/data/ -> project root is three levels up
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Set the Django settings module
# We need to find the settings module. Usually it's project_name.settings
# Let's check for a directory with settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_service.settings')

django.setup()

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


def load_users_from_csv(csv_path=None):
    """
    Read users.csv and create users if they don't exist, assigning them to their group.

    CSV columns: name, username, group

    Args:
        csv_path: Path to the CSV file. Defaults to 'users.csv' in the same directory.

    Returns:
        dict with 'created', 'existing', 'errors' counts.
    """
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.csv')

    stats = {'created': 0, 'existing': 0, 'errors': 0}

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name'].strip()
            username = row['username'].strip()
            group_name = row['group'].strip()

            try:
                # Get or create the group
                group, _ = Group.objects.get_or_create(name=group_name)

                # Get or create the user by username
                user, created = User.objects.get_or_create(username=username)

                if created:
                    # New user — set name and email
                    user.email = username
                    # Split full name into first_name and last_name (first word + rest)
                    name_parts = name.split(' ', 1)
                    user.first_name = name_parts[0]
                    user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                    user.is_staff = True  # allow admin login
                    user.save()
                    stats['created'] += 1
                else:
                    stats['existing'] += 1

                # Add user to group
                user.groups.add(group)

            except Exception as e:
                stats['errors'] += 1
                print(f"Error processing {username}: {e}")

    print(f"Users loaded: {stats['created']} created, {stats['existing']} existing, {stats['errors']} errors.")
    return stats


def load_dollar_prices_from_csv(csv_path=None, rate_type='official', username=None, verbose=True):
    """
    Import historical dollar buy/sell prices from a CSV into DollarPrice.

    Expected columns (headers are normalized: stripped + lowercased):
        date        — business date, YYYY-MM-DD (or DD/MM/YYYY)
        buy price   — column containing 'buy' (or 'شراء') in its header
        sell price  — column containing 'sell'/'sold' (or 'بيع') in its header

    Values may be quoted and contain spaces/commas (e.g. " 2,726.6609 ").

    Re-runnable: rows matching an existing (date, rate_type, buy, sell)
    combination are skipped.

    Args:
        csv_path: Path to the CSV. Defaults to 'price.csv' in this directory.
        rate_type: 'official' or 'parallel'.
        username: User to set as created_by/updated_by (default: first superuser).
        verbose: Print per-row errors and a summary.

    Returns:
        dict with 'created', 'skipped', 'errors' counts.
    """
    from datetime import datetime
    from decimal import Decimal, InvalidOperation

    from django.contrib.auth import get_user_model
    from prices.models import DollarPrice

    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'price.csv')

    user = None
    if username:
        user = get_user_model().objects.filter(username=username).first()
    if user is None:
        user = get_user_model().objects.filter(is_superuser=True).first()
    if user is None:
        raise ValueError('No user provided and no superuser found — created_by is required.')

    def _parse_date(raw):
        for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
            try:
                return datetime.strptime(raw.strip(), fmt).date()
            except ValueError:
                continue
        raise ValueError(f'invalid date: {raw!r}')

    def _parse_decimal(raw):
        cleaned = str(raw).strip().replace(',', '')
        if not cleaned:
            raise ValueError(f'empty price: {raw!r}')
        return Decimal(cleaned)

    stats = {'created': 0, 'skipped': 0, 'errors': 0}

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = {key.strip().lower(): key for key in (reader.fieldnames or [])}

        date_col = None
        buy_col = None
        sell_col = None
        for normalized, original in headers.items():
            if normalized in ('date', 'التاريخ'):
                date_col = original
            elif 'buy' in normalized or 'شراء' in normalized:
                buy_col = original
            elif 'sell' in normalized or 'sold' in normalized or 'بيع' in normalized:
                sell_col = original

        if not (date_col and buy_col and sell_col):
            raise ValueError(
                f'CSV must have date, buy and sell columns. Found headers: {list(headers)}'
            )

        for row_num, row in enumerate(reader, start=2):
            try:
                price_date = _parse_date(row[date_col])
                # Quantize to 2 decimals to match the DB column (decimal_places=2)
                buy_price = _parse_decimal(row[buy_col]).quantize(Decimal('0.01'))
                sell_price = _parse_decimal(row[sell_col]).quantize(Decimal('0.01'))
            except (ValueError, InvalidOperation, TypeError) as e:
                stats['errors'] += 1
                if verbose:
                    print(f"Line {row_num}: {e}")
                continue

            if DollarPrice.objects.filter(
                date=price_date,
                rate_type=rate_type,
                buy_price_in_sdg=buy_price,
                sell_price_in_sdg=sell_price,
            ).exists():
                stats['skipped'] += 1
                continue

            DollarPrice.objects.create(
                date=price_date,
                rate_type=rate_type,
                buy_price_in_sdg=buy_price,
                sell_price_in_sdg=sell_price,
                created_by=user,
                updated_by=user,
            )
            stats['created'] += 1

    if verbose:
        print(
            f"Dollar prices loaded: {stats['created']} created, "
            f"{stats['skipped']} skipped, {stats['errors']} errors."
        )
    return stats


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Load prices history data')
    parser.add_argument(
        '--csv', default=None,
        help='Path to dollar prices CSV (default: price.csv next to this file)',
    )
    parser.add_argument(
        '--rate-type', choices=('official', 'parallel'), default='official',
        help='Dollar rate type to import as',
    )
    parser.add_argument(
        '--user', default=None,
        help='Username to set as created_by (default: first superuser)',
    )
    args = parser.parse_args()

    if args.csv:
        load_dollar_prices_from_csv(
            csv_path=args.csv, rate_type=args.rate_type, username=args.user,
        )
    else:
        load_users_from_csv()

