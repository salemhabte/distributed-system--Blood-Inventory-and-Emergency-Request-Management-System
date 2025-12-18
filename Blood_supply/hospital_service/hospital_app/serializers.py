# hospital_app/serializers.py
from rest_framework import serializers
from .models import Patient, BloodRequest, HospitalInventory
from django.utils import timezone

class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'age', 'blood_type', 'diagnosis']

class PatientResponseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    patient_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'age', 'blood_type', 'diagnosis', 'patient_id', 'created_at']

class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'age', 'blood_type', 'diagnosis']

class BloodRequestCreateSerializer(serializers.ModelSerializer):
    patient = serializers.UUIDField(write_only=True)  # Accept UUID as string

    class Meta:
        model = BloodRequest
        fields = ['patient', 'blood_type', 'units_required', 'priority', 'notes']

    def create(self, validated_data):
        # Convert the UUID string to a Patient instance
        patient_id = validated_data.pop('patient')
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            raise serializers.ValidationError({"patient": "Patient with this ID does not exist."})
        
        blood_request = BloodRequest.objects.create(patient=patient, **validated_data)
        return blood_request

class BloodRequestResponseSerializer(serializers.ModelSerializer):
    request_id = serializers.UUIDField(read_only=True)
    patient_id = serializers.UUIDField(source='patient.patient_id', read_only=True)
    submitted_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = BloodRequest
        fields = ['request_id', 'patient_id', 'blood_type', 'units_required', 'priority', 'status', 'submitted_at']

class HospitalInventoryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalInventory
        fields = ['blood_type', 'quantity']

class HospitalInventoryUpdateSerializer(serializers.Serializer):
    blood_type = serializers.CharField(max_length=5)
    units_received = serializers.IntegerField(min_value=0)