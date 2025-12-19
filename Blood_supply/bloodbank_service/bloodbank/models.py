from django.db import models
from datetime import date

class InventoryItem(models.Model):
    blood_type = models.CharField(max_length=3)
    quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()
    batch_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.blood_type} - {self.batch_number} ({self.quantity} units)"