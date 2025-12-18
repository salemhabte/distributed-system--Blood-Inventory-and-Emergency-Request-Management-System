# hospital_app/urls.py
from django.urls import path
from .views import (
    PatientCreateView, PatientDetailView,
    BloodRequestView,  # ← New combined view
    BloodRequestDetailView,
    HospitalInventoryListView, HospitalInventoryUpdateView,
    api_root  # if you added it
)

urlpatterns = [
    path('', api_root, name='api-root'),  # Optional overview
    path('patients', PatientCreateView.as_view(), name='patient-create'),
    path('patients/<uuid:patient_id>', PatientDetailView.as_view(), name='patient-detail'),
    path('blood-requests', BloodRequestView.as_view(), name='blood-request-list-create'),  # ← Combined
    path('blood-requests/<uuid:request_id>', BloodRequestDetailView.as_view(), name='blood-request-detail'),
    path('inventory', HospitalInventoryListView.as_view(), name='inventory-list'),
    path('inventory/update', HospitalInventoryUpdateView.as_view(), name='inventory-update'),
]