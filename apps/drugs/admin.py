from django.contrib import admin
from .models import Drug, DrugGroup

@admin.register(DrugGroup)
class DrugGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ("name", "dosage_form", "unit", "code", "group")
    search_fields = ("name", "code")
    list_filter = ("group", "dosage_form", "unit")