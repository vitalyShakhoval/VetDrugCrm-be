from django.db import transaction, IntegrityError
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Batch,
    Section,
    BatchSection,
    InventorySession,
    InventorySessionSection,
    InventoryRecord,
)
from .serializers import (
    BatchSerializer,
    InventorySessionSerializer,
    InventoryRecordSerializer,
    InventoryStartSerializer,
)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["batch_number", "drug__name", "drug__code"]
    ordering_fields = ["expiry_date", "batch_number"]
    ordering = ["expiry_date"]


class InventorySessionViewSet(viewsets.ModelViewSet):
    queryset = InventorySession.objects.all().order_by("-started_at")
    serializer_class = InventorySessionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["warehouse__name", "status"]
    ordering_fields = ["started_at", "status"]
    ordering = ["-started_at"]

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        """
        POST /inventory/session/start
        body: {warehouse_id: int, section_ids?: [int], drug_group_id?: int|null}
        """
        s = InventoryStartSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        warehouse_id = data["warehouse_id"]
        section_ids = data.get("section_ids") or []
        drug_group_id = data.get("drug_group_id")

        try:
            with transaction.atomic():
                session = InventorySession.objects.create(
                    warehouse_id=warehouse_id,
                    drug_group_id=drug_group_id,
                )

                if section_ids:
                    sections = list(
                        Section.objects.filter(pk__in=section_ids, warehouse_id=warehouse_id)
                    )
                    if len(sections) != len(set(section_ids)):
                        return Response(
                            {"detail": "Некоторые секции не принадлежат выбранному складу."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    InventorySessionSection.objects.bulk_create(
                        [InventorySessionSection(session=session, section=sec) for sec in sections]
                    )

                bs_qs = BatchSection.objects.filter(batch__warehouse_id=warehouse_id)
                if section_ids:
                    bs_qs = bs_qs.filter(section_id__in=section_ids)
                if drug_group_id is not None:
                    bs_qs = bs_qs.filter(batch__drug__group_id=drug_group_id)

                records = [
                    InventoryRecord(
                        session=session,
                        batch=bs.batch,
                        section=bs.section,
                        expected_quantity=bs.quantity,
                        actual_quantity=None,
                    )
                    for bs in bs_qs.select_related("batch", "section")
                ]
                InventoryRecord.objects.bulk_create(records)

        except IntegrityError:
            return Response(
                {"detail": "На этом складе уже есть активная инвентаризация."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(InventorySessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="discrepancies")
    def discrepancies(self, request, pk=None):
        session = self.get_object()
        qs = session.records.all()

        diff_qs = qs.exclude(difference=0).exclude(difference__isnull=True)
        not_counted = qs.filter(actual_quantity__isnull=True)

        return Response({
            "session": InventorySessionSerializer(session).data,
            "discrepancies": InventoryRecordSerializer(diff_qs, many=True).data,
            "not_counted": InventoryRecordSerializer(not_counted, many=True).data,
        })

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        """
        POST /inventory/session/<pk>/complete
        """
        session = self.get_object()

        if session.status != "in_progress":
            return Response(
                {"detail": "Инвентаризация не в статусе 'in_progress'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.records.filter(actual_quantity__isnull=True).exists():
            return Response(
                {"detail": "Есть непосчитанные строки."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.mark_completed(save=True)
        return Response(InventorySessionSerializer(session).data)

class InventoryRecordViewSet(viewsets.ModelViewSet):
    queryset = InventoryRecord.objects.all().select_related("session", "batch", "section")
    serializer_class = InventoryRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["batch__batch_number", "section__name", "session__warehouse__name"]
    ordering_fields = ["id", "difference"]
    ordering = ["id"]

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /inventory/record/item/<pk>
        body: {"actual_quantity": 12}
        """
        rec = self.get_object()
        if rec.session.status != "in_progress":
            return Response(
                {"detail": "Нельзя менять записи: инвентаризация не активна."},
                status=status.HTTP_400_BAD_REQUEST)

        if set(request.data.keys()) - {"actual_quantity"}:
            return Response(
                {"detail": "Можно обновлять только поле actual_quantity."},
                status=status.HTTP_400_BAD_REQUEST)

        if "actual_quantity" not in request.data:
            return Response(
                {"detail": "Нужно передать actual_quantity."},
                status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)
