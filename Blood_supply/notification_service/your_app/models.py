# Create your models here.
from django.db import models

class Notification(models.Model):
    EVENT_TYPES = [
        ("hospital_request", "Hospital Request"),
        ("request_status", "Request Status"),
        ("low_blood", "Low Blood"),
    ]

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    message = models.TextField()
    hospital_name = models.CharField(max_length=150, null=True, blank=True)
    blood_type = models.CharField(max_length=10, null=True, blank=True)
    units = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    target = models.CharField(max_length=50)  # 'blood_bank' or 'hospital'
    payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} -> {self.target}: {self.message[:60]}"
