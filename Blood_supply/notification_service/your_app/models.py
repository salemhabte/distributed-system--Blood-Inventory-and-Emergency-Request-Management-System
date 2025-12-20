# Create your models here.
from django.db import models

# Table 1: For 'blood-requests' topic
class BloodRequest(models.Model):
    hospital_name = models.CharField(max_length=150)
    hospital_id = models.CharField(max_length=100, null=True, blank=True)
    blood_type = models.CharField(max_length=10)
    quantity = models.IntegerField()
    message = models.TextField()
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'blood_requests'

    def __str__(self):
        return f"Request from {self.hospital_name}: {self.quantity} units of {self.blood_type}"


# Table 2: For 'blood-request-validation' topic
class BloodRequestValidation(models.Model):
    request_id = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=150, null=True, blank=True)
    hospital_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20)  # APPROVED or REJECTED
    message = models.TextField()
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'blood_request_validations'

    def __str__(self):
        return f"Request {self.request_id}: {self.status}"


# Table 3: For 'low-stock-alerts' topic
class LowStockAlert(models.Model):
    blood_type = models.CharField(max_length=10)
    current_units = models.IntegerField()
    threshold = models.IntegerField(null=True, blank=True)
    message = models.TextField()
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'low_stock_alerts'

    def __str__(self):
        return f"Low stock alert: {self.blood_type} - {self.current_units} units"
