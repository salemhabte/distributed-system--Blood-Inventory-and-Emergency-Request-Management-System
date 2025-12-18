from django.db import models
import uuid

class Patient(models.Model):
    patient_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    blood_type = models.CharField(max_length=5)  # e.g., A+, O-
    diagnosis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"

class BloodRequest(models.Model):
    PRIORITY_CHOICES = [
        ('EMERGENCY', 'Emergency'),
        ('URGENT', 'Urgent'),
        ('NORMAL', 'Normal'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
    ]

    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_type = models.CharField(max_length=5)
    units_required = models.PositiveIntegerField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.request_id} - {self.blood_type} ({self.units_required} units)"

class HospitalInventory(models.Model):
    blood_type = models.CharField(max_length=5, unique=True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.blood_type}: {self.quantity} units"