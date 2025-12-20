# hospital_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Patient, BloodRequest, HospitalInventory
from .serializers import (
    PatientCreateSerializer, PatientResponseSerializer, PatientUpdateSerializer,
    BloodRequestCreateSerializer, BloodRequestResponseSerializer,
    HospitalInventoryResponseSerializer, HospitalInventoryUpdateSerializer
)
from .permissions import EmergencyRequestPermissions, BloodRequestPermissions, ReadOnlyForBloodBank
from .kafka_producer import publish_event
from django.db import transaction
import uuid
from django.urls import reverse
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    return Response({
        "patients": request.build_absolute_uri('patient-create'),
        "blood-requests": request.build_absolute_uri('blood-request-list'),
        "inventory": request.build_absolute_uri('inventory-list'),
    })
class PatientCreateView(generics.CreateAPIView):
    """
    API endpoint for creating patient records
    Only hospital staff and admin can create patients
    """
    serializer_class = PatientCreateSerializer
    permission_classes = [IsAuthenticated, EmergencyRequestPermissions]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()

        response_serializer = PatientResponseSerializer(patient)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class PatientDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating patient records
    - GET: All authenticated users can view patients
    - PUT: Only hospital staff and admin can update patients
    """
    serializer_class = PatientResponseSerializer
    permission_classes = [IsAuthenticated, EmergencyRequestPermissions]
    lookup_field = 'patient_id'
    lookup_url_kwarg = 'patient_id'

    def get_queryset(self):
        return Patient.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return PatientUpdateSerializer
        return PatientResponseSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = PatientResponseSerializer(instance)
        return Response(response_serializer.data)

class BloodRequestView(generics.ListCreateAPIView):
    """
    API endpoint for blood request management
    - GET: All authenticated users can view blood requests
    - POST: Only hospital staff and admin can create blood requests
    """
    queryset = BloodRequest.objects.all().order_by('-submitted_at')
    permission_classes = [IsAuthenticated, BloodRequestPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BloodRequestCreateSerializer
        return BloodRequestResponseSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blood_request = serializer.save(status='PENDING')

        response_serializer = BloodRequestResponseSerializer(blood_request)

        # Publish to Kafka
        payload = {
            "request_id": str(blood_request.request_id),
            "patient_id": str(blood_request.patient.patient_id),
            "blood_type": blood_request.blood_type,
            "units_required": blood_request.units_required,
            "priority": blood_request.priority,
            "hospital_id": getattr(request.user, 'organization_name', 'HOSPITAL_UNKNOWN'),
            "submitted_by": request.user.username,
            "submitted_at": blood_request.submitted_at.isoformat()
        }
        publish_event("blood-requests", payload)

        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class BloodRequestDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving individual blood requests
    All authenticated users can view blood requests
    """
    serializer_class = BloodRequestResponseSerializer
    permission_classes = [IsAuthenticated, BloodRequestPermissions]
    lookup_field = 'request_id'
    lookup_url_kwarg = 'request_id'

    def get_queryset(self):
        return BloodRequest.objects.all()

class HospitalInventoryListView(generics.ListAPIView):
    """
    API endpoint for viewing hospital inventory
    All authenticated users can view inventory
    """
    serializer_class = HospitalInventoryResponseSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForBloodBank]

    def get_queryset(self):
        # Ensure all 8 blood types exist
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for bt in blood_types:
            HospitalInventory.objects.get_or_create(blood_type=bt, defaults={'quantity': 0})
        return HospitalInventory.objects.all()

class HospitalInventoryUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating hospital inventory
    Only hospital staff and admin can update inventory
    """
    serializer_class = HospitalInventoryUpdateSerializer
    permission_classes = [IsAuthenticated, EmergencyRequestPermissions]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blood_type = serializer.validated_data['blood_type']
        units = serializer.validated_data['units_received']
        inventory, _ = HospitalInventory.objects.get_or_create(blood_type=blood_type, defaults={'quantity': 0})
        inventory.quantity += units
        inventory.save()

        return Response({
            "message": "Inventory updated successfully",
            "blood_type": blood_type,
            "units_added": units,
            "new_total": inventory.quantity,
            "updated_by": request.user.username,
            "organization": getattr(request.user, 'organization_name', 'Unknown')
        }, status=status.HTTP_200_OK)