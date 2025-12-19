from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer


# Hospital sends requests → fetched by Blood Bank
@api_view(['GET'])
def bloodbank_requests(request):
    qs = Notification.objects.filter(event_type='hospital_request', target='blood_bank').order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)


# Low blood alerts → fetched by Blood Bank
@api_view(['GET'])
def bloodbank_low_blood(request):
    qs = Notification.objects.filter(event_type='low_blood', target='blood_bank').order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)


# Low blood alerts → fetched by Hospital
@api_view(['GET'])
def hospital_low_blood(request):
    hospital_name = request.GET.get('hospital_name')
    if not hospital_name:
        return Response({'error': 'hospital_name is required'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Notification.objects.filter(event_type='low_blood', target='hospital', hospital_name=hospital_name).order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)


# Blood requests approved → fetched by Hospital
@api_view(['GET'])
def hospital_blood_request_approved(request):
    hospital_name = request.GET.get('hospital_name')
    if not hospital_name:
        return Response({'error': 'hospital_name is required'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Notification.objects.filter(event_type='request_status', target='hospital', hospital_name=hospital_name, payload__status='approved').order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)


# Blood requests rejected → fetched by Hospital
@api_view(['GET'])
def hospital_blood_request_rejected(request):
    hospital_name = request.GET.get('hospital_name')
    if not hospital_name:
        return Response({'error': 'hospital_name is required'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Notification.objects.filter(event_type='request_status', target='hospital', hospital_name=hospital_name, payload__status='rejected').order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)
