from rest_framework import serializers
from .models import InventoryItem
from dateutil.parser import parse

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

    def create(self, validated_data):
        expiry_date = parse(validated_data.pop('expiry_date')).date()
        return InventoryItem.objects.create(expiry_date=expiry_date, **validated_data)