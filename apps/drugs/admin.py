from django.contrib import admin
from .models import Drug

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ("name", "dosage_form", "unit", "code")
    search_fields = ("name", "code")
    list_filter = ("dosage_form", "unit")