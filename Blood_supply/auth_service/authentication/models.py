from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based access for blood bank and hospital services
    """
    class Role(models.TextChoices):
        BLOOD_BANK = 'blood_bank', _('Blood Bank')
        HOSPITAL = 'hospital', _('Hospital')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.HOSPITAL,
        help_text=_('User role for access control')
    )

    # Additional fields
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of the organization (blood bank or hospital)')
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text=_('Contact phone number')
    )

    address = models.TextField(
        blank=True,
        help_text=_('Organization address')
    )

    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the user account has been verified')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.organization_name}"

    @property
    def is_blood_bank_staff(self):
        """Check if user is blood bank staff"""
        return self.role == self.Role.BLOOD_BANK

    @property
    def is_hospital_staff(self):
        """Check if user is hospital staff"""
        return self.role == self.Role.HOSPITAL

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == self.Role.ADMIN
