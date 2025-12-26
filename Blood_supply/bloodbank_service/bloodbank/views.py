from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .serializers import InventoryItemSerializer, AddBatchSerializer
from .permissions import BloodBankInventoryPermissions, ReadOnlyForHospital
from .kafka_producer import publish_event
from .inventory_utils import check_and_alert_low_stock

class InventoryListView(generics.ListCreateAPIView):
    """
    API endpoint for blood inventory management
    - GET: List all inventory items (all authenticated users)
    - POST: Add new blood batch (blood bank staff and admin only)
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, BloodBankInventoryPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddBatchSerializer
        return InventoryItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Publish event to Kafka
        publish_event('blood-inventory-updated', {
            'action': 'batch_added',
            'batch_data': serializer.data,
            'updated_by': request.user.username,
            'organization': getattr(request.user, 'organization_name', 'Unknown')
        })

        # Check for low stock after adding batch
        check_and_alert_low_stock(serializer.instance.blood_type)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Blood batch added successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    

class ValidateRequestView(APIView):
    """
    API endpoint for validating and processing blood requests
    Only blood bank staff and admin can process requests
    """
    permission_classes = [IsAuthenticated, BloodBankInventoryPermissions]

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
            units_allocated = data['units_required']
            allocated_items = []

            for item in InventoryItem.objects.filter(blood_type=data['blood_type']).order_by('expiry_date'):
                if item.quantity >= units_allocated:
                    item.quantity -= units_allocated
                    item.save()
                    allocated_items.append({
                        'batch_id': item.id,
                        'units_allocated': units_allocated
                    })
                    break
                else:
                    allocated_units = item.quantity
                    allocated_items.append({
                        'batch_id': item.id,
                        'units_allocated': allocated_units
                    })
                    units_allocated -= allocated_units
                    item.quantity = 0
                    item.save()

            response = {
                'request_id': data['request_id'],
                'status': 'APPROVED',
                'units_allocated': data['units_required'],
                'allocated_at': timezone.now().isoformat(),
                'allocated_by': request.user.username,
                'organization': getattr(request.user, 'organization_name', 'Unknown'),
                'allocation_details': allocated_items
            }
            
            # Check for low stock after processing request
            check_and_alert_low_stock(data['blood_type'])
        else:
            response = {
                'request_id': data['request_id'],
                'status': 'REJECTED',
                'reason': 'Insufficient stock',
                'available_units': available,
                'requested_units': data['units_required'],
                'rejected_at': timezone.now().isoformat(),
                'rejected_by': request.user.username
            }

        publish_event('blood-request-validation', response)
        return Response(response, status=status.HTTP_200_OK)