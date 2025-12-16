from django.urls import path
from .views import bloodbank_requests, bloodbank_low_blood, hospital_notifications

urlpatterns = [
    path('blood-bank/requests/', bloodbank_requests, name='bloodbank-requests'),
    path('blood-bank/low-blood/', bloodbank_low_blood, name='bloodbank-low-blood'),
    path('hospital/', hospital_notifications, name='hospital-notifications'),
]
