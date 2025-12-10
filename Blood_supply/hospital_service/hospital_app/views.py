import uuid
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BloodRequestSerializer
from .kafka_producer import send_event

@api_view(['POST'])
def create_blood_request(request):
    request_id = str(uuid.uuid4())

    data = {
        "request_id": request_id,
        "hospital_id": request.data.get("hospitalId"),
        "blood_type": request.data.get("bloodType"),
        "quantity": request.data.get("quantity"),
        "reason": request.data.get("reason", ""),
        "timestamp": datetime.utcnow().isoformat()
    }

    serializer = BloodRequestSerializer(data=data)

    if serializer.is_valid():

        # 💥 NO DATABASE SAVE HERE
        # serializer.save()  ← REMOVE THIS

        # ✔ Send Kafka event
        send_event("hospital.blood.requested", serializer.validated_data)

        return Response(
            {"message": "Blood request created", "data": serializer.validated_data},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
