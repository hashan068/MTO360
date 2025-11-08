from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComponentViewSet, PurchaseRequisitionViewSet, PurchaseOrderViewSet, SupplierViewSet, ReplenishTransactionViewSet, ConsumptionTransactionViewSet

router = DefaultRouter()
router.register(r'components', ComponentViewSet)
router.register(r'purchase-requisitions', PurchaseRequisitionViewSet)

router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'replenish-transactions', ReplenishTransactionViewSet)
router.register(r'consumption-transactions', ConsumptionTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
