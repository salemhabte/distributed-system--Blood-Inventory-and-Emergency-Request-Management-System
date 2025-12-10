from rest_framework import serializers

class BloodRequestSerializer(serializers.Serializer):
    request_id = serializers.CharField()
    hospital_id = serializers.CharField()
    blood_type = serializers.CharField()
    quantity = serializers.IntegerField()
    reason = serializers.CharField(allow_blank=True)
    timestamp = serializers.CharField()

