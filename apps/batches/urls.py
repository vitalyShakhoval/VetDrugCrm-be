from django.urls import path
from .views import (
    BatchViewSet,
    InventorySessionViewSet
)

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

inventory_session_list = InventorySessionViewSet.as_view({
    "get": "list",
    "post": "create",
})

inventory_session_detail = InventorySessionViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

inventory_session_start = InventorySessionViewSet.as_view({
    "post": "start",
})

inventory_session_discrepancies = InventorySessionViewSet.as_view({
    "get": "discrepancies",
})

inventory_session_complete = InventorySessionViewSet.as_view({
    "post": "complete",
})

inventory_record_list = InventoryRecordViewSet.as_view({
    "get": "list",
    "post": "create",
})

inventory_record_detail = InventoryRecordViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})


urlpatterns = [
    path("batch/list", batch_list, name="batch-list"),
    path("batch/item/<int:pk>", batch_detail, name="batch-item"),
    path("inventory/session/list", inventory_session_list, name="inventory-session-list"),
    path("inventory/session/item/<int:pk>", inventory_session_detail, name="inventory-session-item"),
    path("inventory/session/start", inventory_session_start, name="inventory-session-start"),
    path("inventory/session/item/<int:pk>/discrepancies", inventory_session_discrepancies, name="inventory-session-discrepancies"),
    path("inventory/session/item/<int:pk>/complete", inventory_session_complete, name="inventory-session-complete"),
    path("inventory/record/list", inventory_record_list, name="inventory-record-list"),
    path("inventory/record/item/<int:pk>", inventory_record_detail, name="inventory-record-item"),
]

