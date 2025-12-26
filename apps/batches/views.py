from rest_framework import viewsets, filters
from .models import Batch
from .serializers import BatchSerializer
import pandas as pd
from django.http import HttpResponse

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["batch_number", "drug__name", "drug__code"]
    ordering_fields = ["expiry_date", "batch_number"]
    ordering = ["expiry_date"]

def export_batch_to_excel(request):
    batch = Batch.objects.all().values()

    df = pd.DataFrame(list(batch))

    respone = HttpResponse(content = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    respone['Content-Disposition'] = 'attachment; filename=persons.xlsx'
    df.to_excel(respone,index=False)