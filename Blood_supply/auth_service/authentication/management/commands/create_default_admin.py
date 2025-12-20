from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import User


class Command(BaseCommand):
    help = 'Create default blood bank admin user'

    def handle(self, *args, **options):
        User = get_user_model()

        # Check if admin user already exists
        if User.objects.filter(username='bloodbank_admin').exists():
            self.stdout.write(
                self.style.WARNING('Blood bank admin user already exists')
            )
            return

        # Create default blood bank admin user
        admin_user = User.objects.create_user(
            username='bloodbank_admin',
            email='admin@bloodbank.com',
            password='admin123',
            first_name='Blood',
            last_name='Bank',
            role=User.Role.BLOOD_BANK,
            organization_name='Central Blood Bank',
            phone_number='+1-555-0123',
            address='123 Medical Center Drive, Blood Bank City, BC 12345',
            is_verified=True,
            is_staff=True,
            is_superuser=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created blood bank admin user: {admin_user.username}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Username: bloodbank_admin'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Password: admin123'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'IMPORTANT: Change the default password after first login!'
            )
        )
