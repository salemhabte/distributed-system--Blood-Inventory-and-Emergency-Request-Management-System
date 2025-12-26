from django.urls import path
from .views import InventoryListView, ValidateRequestView

urlpatterns = [
    path('inventory/', InventoryListView.as_view(), name='inventory'),
    path('requests/validate/', ValidateRequestView.as_view(), name='validate'),
]