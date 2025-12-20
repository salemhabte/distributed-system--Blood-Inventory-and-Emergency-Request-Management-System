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


class LocalJWTAuthentication(authentication.BaseAuthentication):
    """
    Simple JWT authentication that validates tokens locally
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
        Validate JWT token locally and create a user object
        """
        try:
            # Decode and validate JWT token locally
            access_token = AccessToken(token)

            # Extract user data from token payload
            user_id = access_token.payload.get('user_id')
            username = access_token.payload.get('username')
            email = access_token.payload.get('email', '')
            first_name = access_token.payload.get('first_name', '')
            last_name = access_token.payload.get('last_name', '')
            role = access_token.payload.get('role', 'hospital')
            organization_name = access_token.payload.get('organization_name', '')

            if not user_id or not username:
                raise exceptions.AuthenticationFailed('Token does not contain required user data')

            # Create a pseudo-user object
            user = self._create_user_from_token_data({
                'id': user_id,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'organization_name': organization_name
            }, token)

            return (user, token)

        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token is invalid or expired: {str(e)}')

    def _create_user_from_token_data(self, user_data, token):
        """
        Create a pseudo-user object from token data
        """
        from django.contrib.auth.models import User

        # Create a pseudo-user object with data from token
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_active=True,
            is_staff=False,
            is_superuser=False
        )

        # Set additional attributes
        user.role = user_data.get('role', 'hospital')
        user.organization_name = user_data.get('organization_name', '')
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
