from django.db import models
from django.core.validators import MinValueValidator

BLOOD_TYPES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

REQUEST_STATUS = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

PRIORITY_CHOICES = [
    ('EMERGENCY', 'Emergency'),
    ('SCHEDULED', 'Scheduled'),
]


class Patient(models.Model):
    """Model to track hospital patients"""
    patient_id = models.CharField(max_length=100, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(0)])
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    diagnosis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"


class BloodRequest(models.Model):
    """Model to track blood requests made by the hospital"""
    request_id = models.CharField(max_length=100, unique=True, db_index=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    units_required = models.IntegerField(validators=[MinValueValidator(1)])
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Blood Request"
        verbose_name_plural = "Blood Requests"
    
    def __str__(self):
        return f"Request {self.request_id} - {self.blood_type} x{self.units_required} - {self.status}"


class HospitalInventory(models.Model):
    """Model to track local hospital blood inventory"""
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['blood_type']
        verbose_name = "Hospital Inventory Item"
        verbose_name_plural = "Hospital Inventory"
        unique_together = [['blood_type', 'batch_number']]
    
    def __str__(self):
        return f"{self.blood_type}: {self.quantity} units"
