from django.contrib import admin
from .models import Patient 


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'age', 'blood_type', 'created_at']
    list_filter = ['blood_type', 'created_at']
    search_fields = ['patient_id', 'first_name', 'last_name']
    readonly_fields = ['patient_id', 'created_at']
    ordering = ['-created_at']
 
