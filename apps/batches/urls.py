from django.urls import path
from .views import BatchViewSet, BatchImportView


batch_list = BatchViewSet.as_view({
    "get": "list",
    "post": "create",
})

batch_detail = BatchViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("batch/list", batch_list, name="batch-list"),
    path("batch/item/<int:pk>", batch_detail, name="batch-item"),
    path("batch/export", BatchImportView, name="export-batch"),
    
]
