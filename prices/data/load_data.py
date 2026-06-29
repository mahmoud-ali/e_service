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


if __name__ == '__main__':
    load_users_from_csv()

