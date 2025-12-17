from rest_framework import serializers
from .models import Patient 


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
 