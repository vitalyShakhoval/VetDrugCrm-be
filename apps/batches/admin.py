from django.contrib import admin

from .models import (
    Warehouse,
    Section,
    Batch,
    BatchSection,
    InventorySession,
    InventoryRecord,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address")
    search_fields = ("name", "address")
    ordering = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "name", "code")
    list_filter = ("warehouse",)
    search_fields = ("name", "code", "warehouse__name")
    ordering = ("warehouse__name", "name")
    list_select_related = ("warehouse",)


class BatchSectionInline(admin.TabularInline):
    model = BatchSection
    extra = 0
    autocomplete_fields = ("section",)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "drug",
        "warehouse",
        "batch_number",
        "expiry_date",
        "remaining_quantity",
        "supplier",
    )
    list_filter = ("warehouse", "expiry_date")
    search_fields = ("batch_number", "drug__name", "drug__code", "supplier")
    ordering = ("-expiry_date", "batch_number")
    list_select_related = ("drug", "warehouse")
    autocomplete_fields = ("drug", "warehouse")
    inlines = [BatchSectionInline]


@admin.register(BatchSection)
class BatchSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "section", "quantity")
    list_filter = ("section__warehouse", "section")
    search_fields = (
        "batch__batch_number",
        "batch__drug__name",
        "batch__drug__code",
        "section__name",
        "section__warehouse__name",
    )
    list_select_related = ("batch", "section", "section__warehouse")
    autocomplete_fields = ("batch", "section")


class InventorySessionSectionInline(admin.TabularInline):
    model = InventorySession.sections.through
    extra = 0
    autocomplete_fields = ("section",)


class InventoryRecordInline(admin.TabularInline):
    model = InventoryRecord
    extra = 0
    can_delete = False

    fields = ("batch", "section", "expected_quantity", "actual_quantity", "difference")
    readonly_fields = ("batch", "section", "expected_quantity", "difference")


@admin.register(InventorySession)
class InventorySessionAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "status", "started_at", "completed_at", "records_count")
    list_filter = ("status", "warehouse")
    search_fields = ("warehouse__name",)
    ordering = ("-started_at",)
    list_select_related = ("warehouse", "drug_group")
    autocomplete_fields = ("warehouse", "drug_group")

    inlines = [InventorySessionSectionInline, InventoryRecordInline]

    @admin.display(description="Строк", ordering=None)
    def records_count(self, obj: InventorySession) -> int:
        return obj.records.count()


@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "batch",
        "section",
        "expected_quantity",
        "actual_quantity",
        "difference",
    )
    list_filter = ("session__warehouse", "session__status", "section")
    search_fields = ("batch__batch_number", "batch__drug__name", "batch__drug__code")
    list_select_related = ("session", "batch", "section", "session__warehouse")
    autocomplete_fields = ("session", "batch", "section")
