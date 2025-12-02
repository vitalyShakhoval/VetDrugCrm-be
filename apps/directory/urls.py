from django.urls import path
from .views import DrugViewSet

drug_list = DrugViewSet.as_view({
    "get": "list",
    "post": "create",
})

drug_detail = DrugViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("drug/list", drug_list, name="drug-list"),
    path("drug/item/<int:pk>", drug_detail, name="drug-item"),
]
