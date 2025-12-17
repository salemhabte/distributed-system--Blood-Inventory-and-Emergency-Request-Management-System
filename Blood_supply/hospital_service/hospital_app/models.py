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
 

 
