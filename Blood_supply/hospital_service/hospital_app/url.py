from django.urls import path
from .views import (
    create_patient, update_patient,
    create_blood_request, get_blood_request,
    get_hospital_inventory, update_hospital_inventory
)

urlpatterns = [
    # Patient endpoints
    path("patients/", create_patient, name="create-patient"),
    path("patients/<str:patientId>/", update_patient, name="get-or-update-patient"),
    
    # Blood request endpoints
    path("blood-requests/", create_blood_request, name="create-or-list-blood-request"),  # POST and GET
    path("blood-requests/<str:requestId>/", get_blood_request, name="get-blood-request"),
    
    # Inventory endpoints
    path("inventory/", get_hospital_inventory, name="get-hospital-inventory"),
    path("inventory/update/", update_hospital_inventory, name="update-hospital-inventory"),
]
