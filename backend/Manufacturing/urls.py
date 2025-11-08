from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManufacturingOrderViewSet, MaterialRequisitionViewSet, BillOfMaterialViewSet, BOMItemViewSet

router = DefaultRouter()
router.register(r'manufacturing-orders', ManufacturingOrderViewSet)
router.register(r'material-requisitions', MaterialRequisitionViewSet)
router.register(r'bills-of-material', BillOfMaterialViewSet)
router.register(r'bom-items', BOMItemViewSet)

urlpatterns = [

    path('', include(router.urls)),
]