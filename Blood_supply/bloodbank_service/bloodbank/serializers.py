from rest_framework import serializers
from .models import InventoryItem
from dateutil.parser import parse
from django.utils import timezone

class InventoryItemSerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = InventoryItem
        fields = ['blood_type', 'quantity', 'expiry_date', 'batch_number']

class AddBatchSerializer(serializers.Serializer):
    blood_type = serializers.CharField(max_length=3)
    quantity = serializers.IntegerField(min_value=1)
    expiry_date = serializers.CharField()
    batch_number = serializers.CharField(max_length=50)

    def validate_blood_type(self, value):
        valid_blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if value not in valid_blood_types:
            raise serializers.ValidationError("Invalid blood type. Must be one of: " + ", ".join(valid_blood_types))
        return value

    def validate_expiry_date(self, value):
        try:
            expiry_date = parse(value).date()
        except ValueError:
            raise serializers.ValidationError("Invalid date format for expiry_date. Use YYYY-MM-DD.")

        if expiry_date <= timezone.now().date():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value

    def validate_batch_number(self, value):
        if InventoryItem.objects.filter(batch_number=value).exists():
            raise serializers.ValidationError("Batch number must be unique.")
        return value

    def create(self, validated_data):
        expiry_date = parse(validated_data.pop('expiry_date')).date()
        return InventoryItem.objects.create(expiry_date=expiry_date, **validated_data)