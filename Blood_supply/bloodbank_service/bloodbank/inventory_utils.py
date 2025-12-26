"""
Utility functions for inventory management
"""
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .kafka_producer import publish_event
import os

# Low stock threshold (configurable via environment variable)
LOW_STOCK_THRESHOLD = int(os.getenv('LOW_STOCK_THRESHOLD', '10'))


def check_and_alert_low_stock(blood_type):
    """Check if stock is low and publish alert if needed"""
    try:
        # Calculate total available units (non-expired)
        total_available = (
            InventoryItem.objects.filter(
                blood_type=blood_type,
                expiry_date__gt=timezone.now().date()
            ).aggregate(total=models.Sum('quantity'))['total'] or 0
        )
        
        # Check if below threshold
        if total_available <= LOW_STOCK_THRESHOLD:
            alert_payload = {
                'blood_type': blood_type,
                'current_units': total_available,
                'threshold': LOW_STOCK_THRESHOLD,
                'alert_type': 'low_stock',
                'timestamp': timezone.now().isoformat(),
                'organization': 'blood_bank'
            }
            
            # Publish low stock alert
            publish_event('low_blood_alert', alert_payload)
            print(f"[Low Stock Alert] Published alert for {blood_type}: {total_available} units (threshold: {LOW_STOCK_THRESHOLD})")
            return True
        return False
    except Exception as e:
        print(f"[Low Stock Alert] Error checking low stock: {e}")
        return False

