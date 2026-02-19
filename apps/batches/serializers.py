from rest_framework import serializers
from .models import (Batch, Warehouse, Section, InventorySession, InventoryRecord, InventorySessionSection, BatchSection,)


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"

class InventorySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySession
        fields = "__all__"
        read_only_fields = ("started_at", "completed_at")


class InventoryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryRecord
        fields = "__all__"
        read_only_fields = ("session", "batch", "section", "difference",)


class InventoryRecordActualSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryRecord
        fields = ("actual_quantity",)

class InventoryStartSerializer(serializers.Serializer):
    warehouse_id = serializers.IntegerField()
    section_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    drug_group_id = serializers.IntegerField(required=False, allow_null=True)