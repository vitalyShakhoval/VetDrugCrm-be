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

    def update(self, instance, validated_data):
        instance.actual_quantity = validated_data.get("actual_quantity", instance.actual_quantity)
        if instance.actual_quantity is None:
            instance.difference = None
        else:
            instance.difference = int(instance.actual_quantity) - int(instance.expected_quantity)
        instance.save(update_fields=["actual_quantity", "difference"])
        return instance


class InventoryStartSerializer(serializers.Serializer):
    warehouse_id = serializers.IntegerField()
    section_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    drug_group_id = serializers.IntegerField(required=False, allow_null=True)
