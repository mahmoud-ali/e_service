import csv
import os
import sys
import django

# Add the project root to sys.path
# Assuming the script is in gold_travel_traditional/data/load_data.py and project root is two levels up
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Set the Django settings module
# We need to find the settings module. Usually it's project_name.settings
# Let's check for a directory with settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_service.settings')

try:
    django.setup()
except Exception as e:
    # If core.settings fails, try to find it
    print(f"Failed to setup django with core.settings: {e}")
    # You might need to adjust this if your settings module has a different name

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from gold_travel_traditional.models import GoldTravelTraditionalUser
from company_profile.models import LkpState

User = get_user_model()

def load_users_from_csv(file_path, state_name="gold_travel_traditional_state"):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Ensure the group exists
    group = Group.objects.get(name='gold_travel_traditional_state')

    # Ensure the state exists (based on name or create one if missing)
    # The requirement says 'add all users to group "gold_travel_traditional_state"'
    # But GoldTravelTraditionalUser model ALSO requires a state (LkpState).
    # I will look for a state named 'gold_travel_traditional_state' or similar if it fits.
    # Actually, the user asked to add them to a GROUP.
    
    # Try to find a default state to use for GoldTravelTraditionalUser
    # If not found, we might need to create one or ask. 
    # For now, I'll try to get or create a LkpState with that name too if it makes sense, 
    # or just use the first one available if any.
    
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # Expected columns: name, username, email, password
        for row in reader:
            username = row.get('username')
            password = row.get('password')
            name = row.get('name')
            email = row.get('email')
            state_id = row.get('state_id')

            state = LkpState.objects.get(id=state_id)
            if not state:
                print("Warning: No LkpState found in database. GoldTravelTraditionalUser creation might fail.")

            if not username or not password:
                print(f"Skipping row missing username or password: {row}")
                continue

            # Create or update User
            user, created = User.objects.get_or_create(username=username,defaults={'email':email})
            if created:
                user.set_password(password)
                user.email = email
                user.save()
                print(f"Created user: {username}")
            else:
                print(f"User already exists: {username}")

            # Add to group
            user.groups.add(group)

            # Create GoldTravelTraditionalUser profile if it doesn't exist
            if state:
                gt_user, gt_created = GoldTravelTraditionalUser.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': name or username,
                        'state': state,
                        'created_by': user, # Using themselves as creator if it's a bootstrap
                        'updated_by': user
                    }
                )
                if gt_created:
                    print(f"Created GoldTravelTraditionalUser profile for: {username}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_data.py <path_to_csv>")
    else:
        load_users_from_csv(sys.argv[1])
