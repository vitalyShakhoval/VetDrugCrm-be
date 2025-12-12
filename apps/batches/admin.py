from django.contrib import admin
from .models import Batch


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("drug", "batch_number", "expiry_date", "remaining_quantity")
    list_filter = ("drug", "expiry_date")
    search_fields = ("batch_number", "drug__name", "drug__code")
