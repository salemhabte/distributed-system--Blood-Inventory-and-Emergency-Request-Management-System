import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.tokens import AccessToken


class ExternalAuthService:
    """
    Service to communicate with the external authentication service
    """

    @staticmethod
    def verify_token(token_string):
        """
        Verify token with auth service
        """
        try:
            url = f"{settings.AUTH_SERVICE_URL}/api/auth/verify-token/"
            headers = {
                'Authorization': f'Bearer {token_string}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('user'), True
            else:
                return None, False

        except requests.RequestException:
            # If auth service is down, deny access
            return None, False

    @staticmethod
    def get_user_permissions(user_data):
        """
        Extract permissions from user data based on role
        """
        role = user_data.get('role')
        permissions = []

        if role == 'blood_bank':
            permissions.extend([
                'bloodbank.view_bloodinventory',
                'bloodbank.add_bloodinventory',
                'bloodbank.change_bloodinventory',
                'bloodbank.delete_bloodinventory',
            ])
        elif role == 'hospital':
            permissions.extend([
                'bloodbank.view_bloodinventory',
                # Hospitals can only view, not modify
            ])
        elif role == 'admin':
            permissions.extend([
                'bloodbank.view_bloodinventory',
                'bloodbank.add_bloodinventory',
                'bloodbank.change_bloodinventory',
                'bloodbank.delete_bloodinventory',
            ])

        return permissions


class ExternalJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication that validates tokens against external auth service
    """

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b'bearer':
            return None

        if len(auth_header) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        """
        Try to authenticate the given credentials. If authentication is successful,
        return a user object and token. If unsuccessful, throw an error.
        """
        try:
            # First try to decode token locally (for basic validation)
            access_token = AccessToken(token)

            # Then verify with auth service
            user_data, is_valid = ExternalAuthService.verify_token(token)

            if not is_valid or not user_data:
                raise exceptions.AuthenticationFailed('Token is invalid or expired')

            # Create a pseudo-user object with the data from auth service
            user = self._create_user_from_auth_data(user_data, token)

            return (user, token)

        except Exception as e:
            raise exceptions.AuthenticationFailed('Token is invalid or expired')

    def _create_user_from_auth_data(self, user_data, token):
        """
        Create a pseudo-user object from auth service data
        """
        from django.contrib.auth.models import User

        # Try to get or create a local user representation
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
            }
        )

        # Set additional attributes from auth service
        user.role = user_data.get('role')
        user.organization_name = user_data.get('organization_name')
        user.is_verified = user_data.get('is_verified', False)
        user.auth_token = token

        return user


class BloodBankPermissionMixin:
    """
    Mixin to check if user has blood bank role
    """

    def has_blood_bank_permission(self, user):
        """Check if user has blood bank role"""
        return hasattr(user, 'role') and user.role == 'blood_bank'

    def has_admin_permission(self, user):
        """Check if user has admin role"""
        return hasattr(user, 'role') and user.role == 'admin'
