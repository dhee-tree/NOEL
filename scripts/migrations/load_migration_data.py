"""
Load data into new database
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noelProject.settings')
django.setup()

from django.contrib.auth.models import User
from Profile.models import UserProfile
from Group.models import SantaGroup, GroupMember, Pick
from Wishlist.models import Wishlist, WishlistItem
from django.db import transaction

print("Loading migration data...")
with open('migration_data.json', 'r') as f:
    data = json.load(f)

print(f"Data loaded: {len(data['users'])} users, {len(data['profiles'])} profiles")

@transaction.atomic
def migrate():
    from django.db import connection
    from datetime import datetime
    
    # Clear existing data
    print("\nClearing existing data...")
    with connection.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE "Wishlist_wishlistitem" CASCADE;')
        cursor.execute('TRUNCATE TABLE "Wishlist_wishlist" CASCADE;')
        cursor.execute('TRUNCATE TABLE "Group_pick" CASCADE;')
        cursor.execute('TRUNCATE TABLE "Group_groupmember" CASCADE;')
        cursor.execute('TRUNCATE TABLE "Group_santagroup" CASCADE;')
        cursor.execute('TRUNCATE TABLE "Profile_userprofile" CASCADE;')
        cursor.execute('TRUNCATE TABLE auth_user CASCADE;')
        print("✓ Tables truncated")
    
    print("\nInserting users with raw SQL...")
    with connection.cursor() as cursor:
        for user_data in data['users']:
            cursor.execute('''
                INSERT INTO auth_user (id, password, last_login, is_superuser, username, 
                                      first_name, last_name, email, is_staff, is_active, date_joined)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', [
                user_data['id'], user_data['password'], user_data.get('last_login'),
                user_data['is_superuser'], user_data['username'], user_data['first_name'],
                user_data['last_name'], user_data['email'], user_data['is_staff'],
                user_data['is_active'], user_data['date_joined']
            ])
    print(f"✓ Created {len(data['users'])} users")
    
    print("Inserting profiles with raw SQL...")
    with connection.cursor() as cursor:
        for profile_data in data['profiles']:
            cursor.execute('''
                INSERT INTO "Profile_userprofile" (id, uuid, google_id, user_id, role, full_name,
                                                   gender, address, profile_pic, is_verified,
                                                   verification_code, date_created, date_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', [
                profile_data['id'], profile_data['uuid'], profile_data.get('google_id'),
                profile_data['user_id'], profile_data['role'], profile_data['full_name'],
                profile_data['gender'], profile_data['address'], profile_data['profile_pic'],
                profile_data['is_verified'], profile_data['verification_code'],
                profile_data['date_created'], profile_data['date_updated']
            ])
    print(f"✓ Created {len(data['profiles'])} profiles")
    
    # Update sequences
    with connection.cursor() as cursor:
        cursor.execute("SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));")
        cursor.execute('SELECT setval(\'"Profile_userprofile_id_seq"\', (SELECT MAX(id) FROM "Profile_userprofile"));')
    print("✓ Sequences updated")
    
    print("Creating groups...")
    for group_data in data['groups']:
        # Get created_by user profile
        created_by_id = group_data['created_by_id']
        group_data['created_by_id'] = created_by_id
        SantaGroup.objects.create(**group_data)
    print(f"✓ Created {len(data['groups'])} groups")
    
    print("Creating group members...")
    for member_data in data['members']:
        GroupMember.objects.create(**member_data)
    print(f"✓ Created {len(data['members'])} members")
    
    print("Creating picks...")
    for pick_data in data['picks']:
        Pick.objects.create(**pick_data)
    print(f"✓ Created {len(data['picks'])} picks")
    
    print("Creating wishlists...")
    for wishlist_data in data['wishlists']:
        Wishlist.objects.create(**wishlist_data)
    print(f"✓ Created {len(data['wishlists'])} wishlists")
    
    print("Creating wishlist items...")
    for item_data in data['wishlist_items']:
        WishlistItem.objects.create(**item_data)
    print(f"✓ Created {len(data['wishlist_items'])} wishlist items")
    
    print("\n✅ Migration complete!")

try:
    migrate()
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
