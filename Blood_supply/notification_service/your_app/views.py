from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
def bloodbank_requests(request):
    qs = Notification.objects.filter(event_type='hospital_request', target='blood_bank')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def bloodbank_low_blood(request):
    qs = Notification.objects.filter(event_type='low_blood', target='blood_bank')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def hospital_notifications(request):
    hospital_name = request.GET.get('hospital_name')
    if not hospital_name:
        return Response({'error': 'hospital_name is required'}, status=status.HTTP_400_BAD_REQUEST)
    qs = Notification.objects.filter(target='hospital', hospital_name=hospital_name)
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)
