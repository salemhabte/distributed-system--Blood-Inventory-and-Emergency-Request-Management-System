from django.urls import path
from .views import (
    create_patient, update_patient
)

urlpatterns = [
    # Patient endpoints
    path("patients/", create_patient, name="create-patient"),
    path("patients/<str:patientId>/", update_patient, name="get-or-update-patient"),
    
]
