import pandas as pd

from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import HttpResponse
from django.db import transaction

from apps.drugs.models import Drug
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
        missing_columns = required_columns-set(df.columns)
        
        if missing_columns:
            return Response(
                {'error':f'Missing required columns: {missing_columns}'},
                status= status.HTTP_400_BAD_REQUEST
                )
        
        #выборка нужных столбцов и их проверка на валидность            
        drug_names = df["drug"].unique()
        drug_map = {
            drug.name: drug
            for drug in Drug.objects.filter(name__in = drug_names)
        }
        valid_items = []
        errors = []

        for index,row in df.iterrows():
            row_number = index + 1
            drug_name = row['drug']
            drug_obj = drug_map.get(drug_name)
            
            if not drug_obj:
                errors.append({
                    "row": row_number,
                    "error": f"Drug not found: {drug_name}"
                })
                continue
            
            try:
                quantity = int(row['remaining_quantity'])
                expiry_date = pd.to_datetime(row['expiry_date']).date()
                purchase_price = float(row["purchase_price"])
            except Exception as e:
                errors.append({
                    "row": row_number,
                    "error": str(e)
                })
                continue

            valid_items.append({
                'drug': drug_obj,
                'series': row['batch_number'],
                'quantity': quantity,
                'expiry_date': expiry_date,
                'supplier': row['supplier'],
                'purchase_price':purchase_price,
            })
        
        #сохранение
        saved_items = []
        if not dry_run and valid_items:
            with transaction.atomic():
               created_objects = Batch.objects.bulk_create([
                    Batch(
                        drug = item['drug'],
                        batch_number = item['series'],
                        quantity = item['quantity'],
                        expiry_date = item['expiry_date'],
                        supplier = item['supplier'],
                        purchase_price = item['purchase_price'],
                        remaining_quantity = item['quantity']
                    )
                    for item in valid_items
                ])
               
            for obj in created_objects:
                saved_items.append({
                    "id": obj.id,
                    "drug": obj.drug.name,
                    "series": obj.batch_number,
                    "quantity": obj.quantity,
                    "expiry_date": obj.expiry_date,
                    "supplier": obj.supplier,
                    "price": obj.purchase_price,
                })
            return Response({
                "dry_run": dry_run,
                "parsed_count": len(valid_items),
                "saved_count": len(saved_items),
                "saved_items": saved_items,
                "errors": errors,
            })
        else:
            preview_items = []
            for item in valid_items:
                preview_items.append({
                    "drug": item["drug"].name,
                    "series": item["series"],
                    "quantity": item["quantity"],
                    "expiry_date": item["expiry_date"],
                    "supplier":item["supplier"],
                    "price": item["purchase_price"],
                })
            return Response({
                "dry_run": dry_run,
                "parsed_count": len(preview_items),
                "valid_items": preview_items,
            })
                
                 