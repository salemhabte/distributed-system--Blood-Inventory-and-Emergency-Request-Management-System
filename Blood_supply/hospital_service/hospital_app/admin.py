from django.contrib import admin
from .models import Patient, BloodRequest, HospitalInventory


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'age', 'blood_type', 'created_at']
    list_filter = ['blood_type', 'created_at']
    search_fields = ['patient_id', 'first_name', 'last_name']
    readonly_fields = ['patient_id', 'created_at']
    ordering = ['-created_at']


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'patient', 'blood_type', 'units_required', 'priority', 'status', 'submitted_at']
    list_filter = ['status', 'priority', 'blood_type', 'submitted_at']
    search_fields = ['request_id', 'patient__patient_id', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['request_id', 'submitted_at', 'updated_at']
    ordering = ['-submitted_at']


@admin.register(HospitalInventory)
class HospitalInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_type', 'quantity', 'batch_number', 'expiry_date', 'last_updated']
    list_filter = ['blood_type', 'expiry_date']
    search_fields = ['blood_type', 'batch_number']
    ordering = ['blood_type']
