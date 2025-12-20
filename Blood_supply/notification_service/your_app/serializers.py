from rest_framework import serializers
from .models import BloodRequest, BloodRequestValidation, LowStockAlert

class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = '__all__'

class BloodRequestValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequestValidation
        fields = '__all__'

class LowStockAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = LowStockAlert
        fields = '__all__'
