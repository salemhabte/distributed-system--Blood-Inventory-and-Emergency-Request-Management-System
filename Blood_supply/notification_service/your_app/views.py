from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BloodRequest, BloodRequestValidation, LowStockAlert
from .serializers import BloodRequestSerializer, BloodRequestValidationSerializer, LowStockAlertSerializer
from django.db import connection

# API 1: Get all blood requests from 'blood-requests' topic
@api_view(['GET'])
def get_blood_requests(request):
    connection.close()
    """Get all blood requests from blood-requests topic (stored in BloodRequest table)"""
    qs = BloodRequest.objects.all().order_by('-created_at')
    serializer = BloodRequestSerializer(qs, many=True)
    return Response({
        'count': qs.count(),
        'data': serializer.data
    })


# API 2: Get all blood request validations from 'blood-request-validation' topic
@api_view(['GET'])
def get_blood_request_validations(request):
    connection.close()
    """Get all blood request validations from blood-request-validation topic (stored in BloodRequestValidation table)"""
    qs = BloodRequestValidation.objects.all().order_by('-created_at')
    serializer = BloodRequestValidationSerializer(qs, many=True)
    return Response({
        'count': qs.count(),
        'data': serializer.data
    })


# API 3: Get all low stock alerts from 'low-stock-alerts' topic
@api_view(['GET'])
def get_low_stock_alerts(request):
    connection.close()
    """Get all low stock alerts from low-stock-alerts topic (stored in LowStockAlert table)"""
    qs = LowStockAlert.objects.all().order_by('-created_at')
    serializer = LowStockAlertSerializer(qs, many=True)
    return Response({
        'count': qs.count(),
        'data': serializer.data
    })
