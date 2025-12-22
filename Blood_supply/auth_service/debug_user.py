import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()

from django.contrib.auth import get_user_model

def check_user(username, password):
    User = get_user_model()
    print(f"Checking user: '{username}'")
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' does NOT exist in the database.")
        print("Existing users:")
        for u in User.objects.all():
            print(f" - {u.username}")
        return

    print(f"✅ User found: ID={user.id}")
    print(f"   - is_active: {user.is_active}")
    print(f"   - is_verified: {user.is_verified}")
    print(f"   - role: {user.role}")
    
    if user.check_password(password):
        print(f"✅ Password '{password}' is CORRECT.")
    else:
        print(f"❌ Password '{password}' is INCORRECT.")

if __name__ == "__main__":
    check_user('demo_hospital', 'demopass123')
