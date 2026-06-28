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
from gold_travel_traditional.models import (
    GoldTravelTraditionalUser,
    GoldTravelTraditionalUserJihatAlaisdar,
    GoldTravelTraditionalUserJihatTarhil,
    LkpJihatAlaisdar,
    LkpJihatAltarhil,
)
from company_profile.models import LkpState

User = get_user_model()

def load_users_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Ensure the group exists (get or create)
    group, _ = Group.objects.get_or_create(name='gold_travel_traditional_state')

    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            username = row.get('username', '').strip()
            password = row.get('password', '').strip()
            name = row.get('name', '').strip()
            state_id = row.get('state_id', '').strip()

            if not username or not password:
                print(f"Skipping row missing username or password: {row}")
                continue

            # Fetch state (required for GoldTravelTraditionalUser)
            try:
                state = LkpState.objects.get(id=state_id)
            except LkpState.DoesNotExist:
                print(f"Skipping {username}: LkpState id={state_id} not found")
                continue

            # Create or update User
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                print(f"Created user: {username}")
            else:
                # Update password even for existing users
                user.set_password(password)
                user.save()
                print(f"User already exists (password updated): {username}")

            # Add to group
            user.groups.add(group)

            # Create GoldTravelTraditionalUser profile if it doesn't exist
            gt_user, gt_created = GoldTravelTraditionalUser.objects.get_or_create(
                user=user,
                defaults={
                    'name': name or username,
                    'state': state,
                    'created_by': user,
                    'updated_by': user
                }
            )
            if gt_created:
                print(f"  Created GoldTravelTraditionalUser profile")
            else:
                print(f"  GoldTravelTraditionalUser profile already exists")

            # Assign jihat based on jiha_type
            jiha_name = row.get('jiha', '').strip()
            jiha_type = row.get('jiha_type', '').strip()
            if jiha_name and jiha_type:
                if jiha_type == '1':
                    jihat, jihat_created = LkpJihatAlaisdar.objects.get_or_create(
                        name=jiha_name,
                        defaults={'state': state},
                    )
                    if jihat_created:
                        print(f"  Created LkpJihatAlaisdar: {jihat.name}")
                    _, assigned = GoldTravelTraditionalUserJihatAlaisdar.objects.get_or_create(
                        master=gt_user,
                        jihat_alaisdar=jihat,
                    )
                    if assigned:
                        print(f"  Assigned jihat_alaisdar: {jihat.name}")
                else:
                    jihat, jihat_created = LkpJihatAltarhil.objects.get_or_create(
                        name=jiha_name,
                        defaults={'state': state},
                    )
                    if jihat_created:
                        print(f"  Created LkpJihatAltarhil: {jihat.name}")
                    _, assigned = GoldTravelTraditionalUserJihatTarhil.objects.get_or_create(
                        master=gt_user,
                        wijhat_altarhil=jihat,
                    )
                    if assigned:
                        print(f"  Assigned wijhat_altarhil: {jihat.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_data.py <path_to_csv>")
    else:
        load_users_from_csv(sys.argv[1])
