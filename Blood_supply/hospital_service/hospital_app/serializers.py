from rest_framework import serializers
from .models import Patient, BloodRequest, HospitalInventory


class PatientCreateSerializer(serializers.Serializer):
    """Serializer for creating a patient"""
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    age = serializers.IntegerField()
    bloodType = serializers.CharField(source='blood_type')
    diagnosis = serializers.CharField(required=False, allow_blank=True)


class PatientUpdateSerializer(serializers.Serializer):
    """Serializer for updating a patient"""
    firstName = serializers.CharField(source='first_name', required=False)
    lastName = serializers.CharField(source='last_name', required=False)
    age = serializers.IntegerField(required=False)
    bloodType = serializers.CharField(source='blood_type', required=False)
    diagnosis = serializers.CharField(required=False, allow_blank=True)


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model (API response format)"""
    patientId = serializers.CharField(source='patient_id', read_only=True)
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    bloodType = serializers.CharField(source='blood_type')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Patient
        fields = ['patientId', 'firstName', 'lastName', 'age', 'bloodType', 'diagnosis', 'createdAt']


class BloodRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating blood requests via API"""
    patientId = serializers.CharField()
    bloodType = serializers.CharField()
    unitsRequired = serializers.IntegerField()
    priority = serializers.ChoiceField(choices=['EMERGENCY', 'SCHEDULED'])
    notes = serializers.CharField(required=False, allow_blank=True)


class BloodRequestSerializer(serializers.ModelSerializer):
    """Serializer for BloodRequest model (API response format)"""
    requestId = serializers.CharField(source='request_id', read_only=True)
    patientId = serializers.CharField(source='patient.patient_id', read_only=True)
    bloodType = serializers.CharField(source='blood_type')
    unitsRequired = serializers.IntegerField(source='units_required')
    submittedAt = serializers.DateTimeField(source='submitted_at', read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = ['requestId', 'patientId', 'bloodType', 'unitsRequired', 'priority', 'status', 'submittedAt']
        read_only_fields = ['requestId', 'status', 'submittedAt']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for HospitalInventory model (API response format)"""
    bloodType = serializers.CharField(source='blood_type')
    expiryDate = serializers.DateField(source='expiry_date', required=False, allow_null=True)
    batchNumber = serializers.CharField(source='batch_number', required=False, allow_blank=True)
    
    class Meta:
        model = HospitalInventory
        fields = ['bloodType', 'quantity', 'expiryDate', 'batchNumber']


class HospitalInventoryUpdateSerializer(serializers.Serializer):
    """Serializer for updating hospital inventory"""
    bloodType = serializers.CharField()
    unitsReceived = serializers.IntegerField(min_value=1)
