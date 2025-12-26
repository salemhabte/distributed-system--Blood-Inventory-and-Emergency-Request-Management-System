from rest_framework import permissions


class IsBloodBankStaff(permissions.BasePermission):
    """
    Custom permission to only allow blood bank staff to access
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role in ['blood_bank', 'admin']
        )


class IsHospitalStaff(permissions.BasePermission):
    """
    Custom permission to only allow hospital staff to access (read-only)
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role == 'hospital'
        )


class IsAdminOrBloodBank(permissions.BasePermission):
    """
    Custom permission to allow admin or blood bank staff to access
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user and
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role in ['blood_bank', 'admin']
        )


class ReadOnlyForHospital(permissions.BasePermission):
    """
    Custom permission that allows hospitals to read but only blood banks/admins to modify
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # All authenticated users can read
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only blood bank and admin can modify
        return user.role in ['blood_bank', 'admin']


class BloodBankInventoryPermissions(permissions.BasePermission):
    """
    Specific permissions for blood inventory management
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # All authenticated users can view inventory
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only blood bank and admin can modify inventory
        return user.role in ['blood_bank', 'admin']

    def has_object_permission(self, request, view, obj):
        user = request.user

        # All authenticated users can view specific inventory items
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only blood bank and admin can modify inventory items
        return hasattr(user, 'role') and user.role in ['blood_bank', 'admin']
