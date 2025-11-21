from rest_framework.routers import DefaultRouter
from .views import DrugViewSet

router = DefaultRouter()
router.register(r"drugs", DrugViewSet, basename="drug")

urlpatterns = router.urls
