from rest_framework import permissions


class IsHospitalStaff(permissions.BasePermission):
    """
    Custom permission to only allow hospital staff to access
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role in ['hospital', 'admin']
        )


class IsBloodBankStaff(permissions.BasePermission):
    """
    Custom permission to only allow blood bank staff to access (read-only for hospital data)
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role == 'blood_bank'
        )


class IsAdminOrHospital(permissions.BasePermission):
    """
    Custom permission to allow admin or hospital staff to access
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role in ['hospital', 'admin']
        )


class ReadOnlyForBloodBank(permissions.BasePermission):
    """
    Custom permission that allows blood banks to read but only hospitals/admins to modify
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # All authenticated users can read
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only hospital and admin can modify
        return user.role in ['hospital', 'admin']


class EmergencyRequestPermissions(permissions.BasePermission):
    """
    Specific permissions for emergency request management
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # All authenticated users can view emergency requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only hospital and admin can create/modify emergency requests
        return user.role in ['hospital', 'admin']

    def has_object_permission(self, request, view, obj):
        user = request.user

        # All authenticated users can view specific emergency requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only hospital and admin can modify emergency requests
        return hasattr(user, 'role') and user.role in ['hospital', 'admin']


class BloodRequestPermissions(permissions.BasePermission):
    """
    Specific permissions for blood request management
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # All authenticated users can view blood requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only hospital and admin can create/modify blood requests
        return user.role in ['hospital', 'admin']

    def has_object_permission(self, request, view, obj):
        user = request.user

        # All authenticated users can view specific blood requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only hospital and admin can modify blood requests
        return hasattr(user, 'role') and user.role in ['hospital', 'admin']
