from django.urls import path
from .views import *

urlpatterns = [
    path('hospital/blood_requests/', bloodbank_requests, name='hospital_blood_requests'),
    path('blood_bank/low_blood/', bloodbank_low_blood, name='bloodbank-low-blood'),
    path('hospital/low_blood/', hospital_low_blood, name='hospital_low_blood'),
    path('hospital/blood_request_approved', hospital_blood_request_approved, name='hospital_blood_request_approved'),
    path('hospital/blood_request_rejected', hospital_blood_request_rejected, name='hospital_blood_request_rejected'),
]
