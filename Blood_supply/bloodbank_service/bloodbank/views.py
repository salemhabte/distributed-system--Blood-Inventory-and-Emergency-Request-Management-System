from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .serializers import InventoryItemSerializer, AddBatchSerializer
from .kafka_producer import publish_event  # We'll create this

class InventoryView(APIView):
    LOW_STOCK_THRESHOLDS = {
        "O-": 15,
        "O+": 12,
        "A-": 8,
        "B-": 8,
        "AB-": 8,
        "A+": 10,
        "B+": 10,
        "AB+": 10,
    }

    def get(self, request):
        items = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddBatchSerializer(data=request.data)
        if serializer.is_valid():
            inventory_item = serializer.save()
            blood_type = inventory_item.blood_type
            current_total_quantity = InventoryItem.objects.filter(blood_type=blood_type).aggregate(total=models.Sum('quantity'))['total'] or 0

            low_stock_threshold = self.LOW_STOCK_THRESHOLDS.get(blood_type, 10) # Default to 10 if blood type not found

            if current_total_quantity < low_stock_threshold:
                publish_event('inventory.lowstock', {
                    'blood_type': blood_type,
                    'current_stock': current_total_quantity,
                    'threshold': low_stock_threshold,
                    'timestamp': timezone.now().isoformat()
                })
            return Response({"message": "Blood batch added successfully", "current_stock": current_total_quantity}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateRequestView(APIView):
    LOW_STOCK_THRESHOLDS = {
        "O-": 15,
        "O+": 12,
        "A-": 8,
        "B-": 8,
        "AB-": 8,
        "A+": 10,
        "B+": 10,
        "AB+": 10,
    }
    def post(self, request):
        data = request.data
        required_fields = ['request_id', 'blood_type', 'units_required', 'hospital_id']
        if not all(field in data for field in required_fields):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        available = InventoryItem.objects.filter(
            blood_type=data['blood_type'],
            expiry_date__gt=timezone.now().date()
        ).aggregate(total=models.Sum('quantity'))['total'] or 0

        if available >= data['units_required']:
            # Simple allocation: deduct from first matching batch
            for item in InventoryItem.objects.filter(blood_type=data['blood_type']).order_by('expiry_date'):
                if item.quantity >= data['units_required']:
                    item.quantity -= data['units_required']
                    item.save()

            # After allocation, check for low stock and publish an alert if necessary
            allocated_blood_type = data['blood_type']
            current_total_quantity = InventoryItem.objects.filter(blood_type=allocated_blood_type).aggregate(total=models.Sum('quantity'))['total'] or 0
            low_stock_threshold = self.LOW_STOCK_THRESHOLDS.get(allocated_blood_type, 10)

            if current_total_quantity < low_stock_threshold:
                publish_event('inventory.lowstock', {
                    'blood_type': allocated_blood_type,
                    'current_stock': current_total_quantity,
                    'threshold': low_stock_threshold,
                    'timestamp': timezone.now().isoformat()
                })

            response = {
                'request_id': data['request_id'],
                'status': 'APPROVED',
                'units_allocated': data['units_required'],
                'allocated_at': timezone.now().isoformat()
            }
        else:
            response = {
                'request_id': data['request_id'],
                'status': 'REJECTED',
                'reason': 'Insufficient stock'
            }

        publish_event('blood-request-validation', response)
        return Response(response, status=status.HTTP_200_OK)