from django.urls import path
from .views import create_blood_request

urlpatterns = [
    path("request-blood/", create_blood_request),
]
