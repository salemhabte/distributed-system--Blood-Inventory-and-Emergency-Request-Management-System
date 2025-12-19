# hospital_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Patient, BloodRequest, HospitalInventory
from .serializers import (
    PatientCreateSerializer, PatientResponseSerializer, PatientUpdateSerializer,
    BloodRequestCreateSerializer, BloodRequestResponseSerializer,
    HospitalInventoryResponseSerializer, HospitalInventoryUpdateSerializer
)
from .kafka_producer import publish_event
from django.db import transaction
import uuid
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        "patients": request.build_absolute_uri('patient-create'),
        "blood-requests": request.build_absolute_uri('blood-request-list'),
        "inventory": request.build_absolute_uri('inventory-list'),
    })
class PatientCreateView(APIView):
    def get(self, request):
        patients = Patient.objects.all()
        serializer = PatientResponseSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientCreateSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            response_serializer = PatientResponseSerializer(patient)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientDetailView(APIView):
    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, patient_id=patient_id)
        serializer = PatientResponseSerializer(patient)
        return Response(serializer.data)

    def put(self, request, patient_id):
        patient = get_object_or_404(Patient, patient_id=patient_id)
        serializer = PatientUpdateSerializer(patient, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PatientResponseSerializer(patient)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BloodRequestView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = BloodRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            blood_request = serializer.save(status='PENDING')
            response_serializer = BloodRequestResponseSerializer(blood_request)

            # Publish to Kafka
            payload = {
                "request_id": str(blood_request.request_id),
                "patient_id": str(blood_request.patient.patient_id),
                "blood_type": blood_request.blood_type,
                "units_required": blood_request.units_required,
                "priority": blood_request.priority,
                "hospital_id": "HOSPITAL_001",
                "submitted_at": blood_request.submitted_at.isoformat()
            }
            publish_event("blood-requests", payload)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        requests = BloodRequest.objects.all().order_by('-submitted_at')
        serializer = BloodRequestResponseSerializer(requests, many=True)
        return Response(serializer.data)

class BloodRequestDetailView(APIView):
    def get(self, request, request_id):
        blood_request = get_object_or_404(BloodRequest, request_id=request_id)
        serializer = BloodRequestResponseSerializer(blood_request)
        return Response(serializer.data)

class HospitalInventoryListView(APIView):
    def get(self, request):
        # Return all blood types, even with 0 quantity
        inventory = HospitalInventory.objects.all()
        # Ensure all 8 blood types exist
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for bt in blood_types:
            HospitalInventory.objects.get_or_create(blood_type=bt, defaults={'quantity': 0})
        inventory = HospitalInventory.objects.all()
        serializer = HospitalInventoryResponseSerializer(inventory, many=True)
        return Response(serializer.data)

class HospitalInventoryUpdateView(APIView):
    def put(self, request):
        serializer = HospitalInventoryUpdateSerializer(data=request.data)
        if serializer.is_valid():
            blood_type = serializer.validated_data['blood_type']
            units = serializer.validated_data['units_received']
            inventory, _ = HospitalInventory.objects.get_or_create(blood_type=blood_type, defaults={'quantity': 0})
            inventory.quantity += units
            inventory.save()
            return Response({"message": "Inventory updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)