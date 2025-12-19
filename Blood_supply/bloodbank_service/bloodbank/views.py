from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .serializers import InventoryItemSerializer, AddBatchSerializer
from .kafka_producer import publish_event  # We'll create this

class InventoryView(APIView):
    def get(self, request):
        items = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddBatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Blood batch added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateRequestView(APIView):
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
                    break
                else:
                    data['units_required'] -= item.quantity
                    item.quantity = 0
                    item.save()

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