from django.urls import path
from .views import InventoryView, ValidateRequestView

urlpatterns = [
    path('inventory', InventoryView.as_view(), name='inventory'),
    path('requests/validate', ValidateRequestView.as_view(), name='validate'),
]