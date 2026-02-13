import pandas as pd
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import HttpResponse
from django.db import transaction
from drugs.models import Drug

from .models import Batch
from .serializers import BatchSerializer


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["batch_number", "drug__name", "drug__code"]
    ordering_fields = ["expiry_date", "batch_number"]
    ordering = ["expiry_date"]

class BatchImportView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):

        file = request.FILES.get('file')
        dry_run = request.data.get('dry_run', 'true').lower() == 'true'

        if not file:
            return Response({'error':'file required'}, status= status.HTTP_400_BAD_REQUEST)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return Response({'error': 'unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error':f'file parse error: {e}'},
                status=status.HTTP_400_BAD_REQUEST  
            )
        
        required_columns = {
            'drug',
            'batch_number',
            'remaining_quantity',
            'expiry_date',
            'supplier',
            'purchase_price',
        }

        if not required_columns.issubset(df.columns):
            return Response(
                {'error':f'Missing required columns: {required_columns}'},
                status= status.HTTP_400_BAD_REQUEST
                )
        
        parsed_item = []

        
        #выборка нужных столбцов и их проверка на валидность            
        for index,row in df.iterrows():
            
            if not Drug.objects.filter(name=row['drug']).exists():
                return Response(
                {'error':f"Missing required drugs: {row['drug']}"},
                status= status.HTTP_400_BAD_REQUEST
            )

            item_data = {
                'name': row['drug'],
                'series':row['batch_number'],
                'quantity':int(row['remaining_quantity']),
                'expiry_date':pd.to_datetime(row['expiry_date']).date(),
                'supplier':row['supplier'],
                'purchase_price':row['purchase_price'],
            }
            #проверка есть ли название таблеток в списке
            parsed_item.append(item_data)

#сохранение
            
        if not dry_run:
            with transaction.atomic():
                for item in parsed_item:
                    batch = Batch.objects.create(
                        drug=Drug.objects.filter(name=item['name']).exists(),
                        series=item['remaning_quantity'],
                        quantity=item['quantity'],
                        expiration_date=item['expiry_date'],
                        supplier=item['supplier'],
                        price=row.item('purchase_price'),
                    )
            return Response(parsed_item)
        
                