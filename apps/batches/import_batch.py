import pandas as pd

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db import transaction

from apps.drugs.models import Drug
from .models import Batch

class BatchImportView(APIView):
    parser_classes = (MultiPartParser, FormParser)   

    def bad_line_handler(self, msg):
        print(msg)
        return

    def safe_row(self,row):
        return {
        'drug': row.get('drug'),
        'series': row.get('batch_number'), 
        'quantity': row.get('remaining_quantity'),
        'expiry_date': row.get('expiry_date'),
        'supplier': row.get('supplier'),
        'purchase_price': row.get('purchase_price'), 
    }
    def post(self, request):
        file = request.FILES.get('file')
        dry_run = request.data.get('dry_run', 'true').lower() == 'true'

        if not file:
            return Response({'error':'file required'}, status= status.HTTP_400_BAD_REQUEST)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, on_bad_lines=self.bad_line_handler)
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
            drug.name.lower(): drug
            for drug in Drug.objects.filter(name__in = drug_names)
        }
        
        valid_items = []
        errors = []
        set_key = set()
        invalid_items = []
        for index,row in df.iterrows():
            try:
                row_number = index + 1
                drug_name = row['drug']
                drug_obj = drug_map.get(drug_name.lower())
                quantity = int(row['remaining_quantity'])
                expiry_date = pd.to_datetime(row['expiry_date']).date()
                purchase_price = float(row["purchase_price"])
                
                if quantity <= 0:
                    errors.append({"row": row_number, "error": "quantity must be positive"})
                    invalid_items.append(self.safe_row(row))
                    continue
                if purchase_price < 0:
                    errors.append({"row": row_number, "error": "price cannot be negative"})
                    invalid_items.append(self.safe_row(row))
                    continue

            except Exception as e:
                safe_row = self.safe_row(row)
                invalid_items.append(safe_row)
                errors.append({
                    "row": row_number,
                    "error": str(e)
                })
                continue

            if not drug_obj:
                safe_row = self.safe_row(row)
                invalid_items.append(safe_row)
                errors.append({
                    "row": row_number,
                    "error": f"Drug not found: {drug_name}"
                })
                continue
            
            #Строки для уникальных записей
            key = (drug_obj, row['batch_number'], expiry_date)

            if key in set_key:
                safe_row = self.safe_row(row)
                invalid_items.append(safe_row)
                errors.append({
                    "row": row_number,
                    "error": f"The recording repeats: {drug_name}"
                })
                continue

            set_key.add(key)

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
        created_objects = []
        preview_items = []
        saved_count = 0
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
                ], ignore_conflicts=True)
               
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
        if dry_run and valid_items:
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
            "valid_count": len(valid_items),
            "saved_count": len(saved_items),
            "saved_items": saved_items,
            "preview_items": preview_items,
            "invalid_count": len(invalid_items),
            "invalid_items": invalid_items,
            "errors_count": len(errors),
            "errors": errors,
        })