from rest_framework import permissions


class IsBloodBankStaff(permissions.BasePermission):
    """
    Custom permission to only allow blood bank staff to access
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_blood_bank_staff
        )


class IsHospitalStaff(permissions.BasePermission):
    """
    Custom permission to only allow hospital staff to access
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_hospital_staff
        )


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsBloodBankOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow blood bank staff or admin to access
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_blood_bank_staff or request.user.is_admin)
        )


class IsHospitalOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow hospital staff or admin to access
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_hospital_staff or request.user.is_admin)
        )
