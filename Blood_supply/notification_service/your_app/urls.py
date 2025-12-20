from django.urls import path
from .views import get_blood_requests, get_blood_request_validations, get_low_stock_alerts

urlpatterns = [
    path('blood-requests/', get_blood_requests, name='get_blood_requests'),
    path('blood-request-validations/', get_blood_request_validations, name='get_blood_request_validations'),
    path('low-stock-alerts/', get_low_stock_alerts, name='get_low_stock_alerts'),
]
