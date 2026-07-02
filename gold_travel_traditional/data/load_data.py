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
    AppMoveGoldTraditional,
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

    # Ensure groups exist
    travel_group, _ = Group.objects.get_or_create(name='gold_travel_traditional_state')
    manager_group, _ = Group.objects.get_or_create(name='gold_travel_traditional_manager_show')

    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            username = row.get('username', '').strip()
            password = row.get('password', '').strip()
            name = row.get('name', '').strip()
            state_id = row.get('state_id', '').strip()
            jiha_type = row.get('jiha_type', '').strip()

            if not username or not password:
                print(f"Skipping row missing username or password: {row}")
                continue

            # Create or update User
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                print(f"Created user: {username}")
            else:
                user.set_password(password)
                user.save()
                print(f"User already exists (password updated): {username}")

            # jiha_type=3: manager — user + manager group only, no profile
            if jiha_type == '3':
                user.groups.add(manager_group)
                print(f"  Added to manager group")
                continue

            # jiha_type=1,2: needs state for profile + jihat
            if not state_id:
                print(f"  WARNING: no state_id — skipping profile/jihat for {username}")
                user.groups.add(travel_group)
                continue

            try:
                state = LkpState.objects.get(id=state_id)
            except LkpState.DoesNotExist:
                print(f"  WARNING: LkpState id={state_id} not found — skipping profile/jihat for {username}")
                user.groups.add(travel_group)
                continue

            # Add to travel group
            user.groups.add(travel_group)

            # Create or update GoldTravelTraditionalUser profile
            user_type = int(row.get('user_type', '0') or '0')
            gt_user, gt_created = GoldTravelTraditionalUser.objects.get_or_create(
                user=user,
                defaults={
                    'name': name or username,
                    'state': state,
                    'user_type': user_type,
                    'created_by': user,
                    'updated_by': user
                }
            )
            if gt_created:
                print(f"  Created GoldTravelTraditionalUser profile")
            elif gt_user.user_type != user_type:
                gt_user.user_type = user_type
                gt_user.save()
                print(f"  Updated user_type to {gt_user.get_user_type_display()}")
            else:
                print(f"  GoldTravelTraditionalUser profile already exists")

            # Assign jihat based on jiha_type
            jiha_name = row.get('jiha', '').strip()
            if jiha_name:
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

def make_users_staff(file_path):
    """Set is_staff=True for all users listed in the CSV."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        updated = 0
        for row in reader:
            username = row.get('username', '').strip()
            if not username:
                continue
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                print(f"  User not found: {username}")
                continue
            if not user.is_staff:
                user.is_staff = True
                user.save()
                updated += 1
        print(f"Made {updated} users staff")

def assign_tarhil_to_alaisdar_users(file_path, wijhat_altarhil_ids):
    """
    For every user in the CSV that has at least one
    GoldTravelTraditionalUserJihatAlaisdar, create a
    GoldTravelTraditionalUserJihatTarhil pointing to each given wijhat_altarhil.

    Accepts a single int or a list of ints.
    """
    if isinstance(wijhat_altarhil_ids, (int, str)):
        wijhat_altarhil_ids = [int(wijhat_altarhil_ids)]

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Fetch all wijhat records
    wijhats = []
    for wid in wijhat_altarhil_ids:
        try:
            wijhats.append(LkpJihatAltarhil.objects.get(id=wid))
        except LkpJihatAltarhil.DoesNotExist:
            print(f"LkpJihatAltarhil id={wid} not found — skipping")

    if not wijhats:
        print("No valid wijhat_altarhil IDs provided")
        return

    # Read usernames from CSV
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        usernames = [row['username'].strip() for row in csv.DictReader(csvfile)]

    # Users from CSV that have at least one GoldTravelTraditionalUserJihatAlaisdar
    master_ids = (
        GoldTravelTraditionalUserJihatAlaisdar.objects
        .filter(master__user__username__in=usernames)
        .values_list('master_id', flat=True)
        .distinct()
    )
    gt_users = GoldTravelTraditionalUser.objects.filter(id__in=master_ids)

    created = 0
    for gt_user in gt_users:
        for wijhat in wijhats:
            _, c = GoldTravelTraditionalUserJihatTarhil.objects.get_or_create(
                master=gt_user,
                wijhat_altarhil=wijhat,
            )
            if c:
                created += 1
                print(f"  Assigned wijhat_altarhil '{wijhat.name}' to {gt_user.user.username}")

    print(f"Assigned tarhil to {created} user-jihat pairs ({len(gt_users)} users x {len(wijhats)} wijhats)")

def drop_app_move_gold():
    """Delete all AppMoveGoldTraditional records (cascades to details)."""
    count, _ = AppMoveGoldTraditional.objects.all().delete()
    print(f"Deleted {count} AppMoveGoldTraditional records")

# jiha_type → user_type mapping
JIHATYPE_TO_USERTYPE = {'1': 1, '2': 2, '3': 4}  # 1=جهة الإصدار, 2=جهة الوصول, 4=مدير الولاية

def add_user_type_to_csv(file_path):
    """Add user_type column to a CSV based on jiha_type mapping."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if 'user_type' in fieldnames:
        print(f"  user_type already exists in {os.path.basename(file_path)}")
        return

    # Insert user_type after jiha_type
    jt_idx = fieldnames.index('jiha_type')
    fieldnames.insert(jt_idx + 1, 'user_type')

    for row in rows:
        jt = row.get('jiha_type', '').strip()
        row['user_type'] = str(JIHATYPE_TO_USERTYPE.get(jt, ''))

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Added user_type to {os.path.basename(file_path)} ({len(rows)} rows)")

def add_user_type_to_all_csvs():
    """Add user_type to all _users.csv files in the data directory."""
    data_dir = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(os.listdir(data_dir)):
        if f.endswith('_users.csv'):
            add_user_type_to_csv(os.path.join(data_dir, f))

def load_and_setup(file_path, wijhat_altarhil_ids=None, make_staff=True):
    """
    Combined: load users from CSV, make them staff, and assign tarhil
    to all users with jihat_alaisdar.
    """
    load_users_from_csv(file_path)
    if make_staff:
        make_users_staff(file_path)
    if wijhat_altarhil_ids is not None:
        assign_tarhil_to_alaisdar_users(file_path, wijhat_altarhil_ids)

def reload_all_csvs():
    """Re-run load_users_from_csv for all _users.csv files."""
    data_dir = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(os.listdir(data_dir)):
        if f.endswith('_users.csv'):
            path = os.path.join(data_dir, f)
            print(f"\n{'='*60}")
            print(f"  {f}")
            print(f"{'='*60}")
            load_users_from_csv(path)

def _parse_ids(raw):
    """Parse '1,2,3' into [1, 2, 3]."""
    return [int(x.strip()) for x in raw.split(',') if x.strip()]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_data.py <path_to_csv> [--staff] [--assign-tarhil <ids>] [--setup <ids>] [--drop-moves] [--add-user-type] [--add-user-type-all]")
        print("  --staff                      Make users staff after loading")
        print("  --assign-tarhil <ids>        Comma-separated wijhat_altarhil IDs (e.g. 1,3,4)")
        print("  --setup <ids>                load + staff + assign-tarhil in one step")
        print("  --drop-moves                 Delete all AppMoveGoldTraditional records")
        print("  --add-user-type              Add user_type column to the given CSV")
        print("  --add-user-type-all          Add user_type column to all _users.csv files")
        print("  --reload-all                 Re-run load_users_from_csv on all _users.csv files")
    else:
        if '--add-user-type-all' in sys.argv:
            add_user_type_to_all_csvs()
        elif '--add-user-type' in sys.argv:
            add_user_type_to_csv(sys.argv[1])
        elif '--reload-all' in sys.argv:
            reload_all_csvs()
        elif '--drop-moves' in sys.argv:
            drop_app_move_gold()
        elif '--setup' in sys.argv:
            idx = sys.argv.index('--setup')
            ids = _parse_ids(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None
            load_and_setup(sys.argv[1], wijhat_altarhil_ids=ids)
        else:
            load_users_from_csv(sys.argv[1])
            if '--staff' in sys.argv:
                make_users_staff(sys.argv[1])
            if '--assign-tarhil' in sys.argv:
                idx = sys.argv.index('--assign-tarhil')
                if idx + 1 < len(sys.argv):
                    assign_tarhil_to_alaisdar_users(sys.argv[1], _parse_ids(sys.argv[idx + 1]))
