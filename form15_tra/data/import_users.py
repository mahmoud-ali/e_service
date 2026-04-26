#!/usr/bin/env python
"""
Script to import users from CSV and create CollectorAssignmentCollector records.
CSV columns: name, username, password
"""

import os
import sys
import csv
import argparse
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

from form15_tra.models import CollectorAssignmentCollector, Market

User = get_user_model()


def import_users(csv_path, skip_existing=True):
    """
    Read CSV and create users and CollectorAssignmentCollector records.
    """
    created = 0
    skipped = 0
    errors = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not {'name', 'username', 'password'} <= set(reader.fieldnames):
            raise ValueError(
                f"CSV must contain columns: name, username, password. "
                f"Found: {reader.fieldnames}"
            )
        
        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            name = row['name'].strip()
            username = row['username'].strip()
            password = row['password'].strip()
            
            if not username:
                errors.append(f"Row {row_num}: username missing")
                continue
            
            # Check if user already exists
            user = None
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if skip_existing:
                    skipped += 1
                    print(f"User '{username}' already exists, skipping...")
                    continue
            
            try:
                if not user:
                    # Create user
                        user = User.objects.create_user(
                            username=username,
                            password=password,
                            first_name=name.split()[0] if name else '',
                            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                        )

                # add user to `form15_tra.collectors` group
                group = Group.objects.get(name='التحصيل الإلكتروني/متحصل')
                print(group)

                user.groups.add(group)
                user.save()

                print(user.groups)

                # Create CollectorAssignmentCollector
                print(f"Creating collector assignment for user '{user.username}', username '{username}', market '{Market.objects.first()}'.")
                collector = CollectorAssignmentCollector.objects.create(
                    user=user,
                    market=Market.objects.first(),
                    esali_username=username,
                    is_collector=True,
                    esali_password_enc="1212"
                )

                collector.set_esali_password_plain(password)
                collector.save()
                
                created += 1
                print(f"Created user '{username}' and collector assignment '{collector}'.")
                
            except Exception as e:
                errors.append(f"Row {row_num}: {e}")

        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {len(errors)}")

    
    return created, skipped, errors


def main():
    parser = argparse.ArgumentParser(
        description="Import users from CSV and create CollectorAssignmentCollector records."
    )
    parser.add_argument(
        'csv_file',
        nargs='?',
        default='users.csv',
        help='Path to CSV file (default: users.csv)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        default=True,
        help='Skip existing users (default: True)'
    )
    parser.add_argument(
        '--no-skip-existing',
        dest='skip_existing',
        action='store_false',
        help='Do not skip existing users, raise error instead'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed output'
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file '{csv_path}' not found.")
        sys.exit(1)
    
    print(f"Importing users from '{csv_path}'...")
    created, skipped, errors = import_users(csv_path, args.skip_existing)
    
    print("\n--- Summary ---")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  {err}")
    
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()