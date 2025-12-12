from rest_framework import viewsets, filters
from .models import Batch
from .serializers import BatchSerializer


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["batch_number", "drug__name", "drug__code"]
    ordering_fields = ["expiry_date", "batch_number"]
    ordering = ["expiry_date"]
