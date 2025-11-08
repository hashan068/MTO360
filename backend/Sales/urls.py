from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

# Register the viewsets for the API endpoints
router.register(r'customers', views.CustomerViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'rfqs', views.RFQViewSet)
router.register(r'rfq-items', views.RFQItemViewSet)
router.register(r'orders', views.SalesOrderViewSet)
router.register(r'order-items', views.SalesOrderItemViewSet)
router.register(r'quotations', views.QuotationViewSet, basename='quotation')
router.register(r'quotation-items', views.QuotationItemViewSet, basename='quotation-item')

urlpatterns = [
    # Include the API endpoints in the URL patterns
    path('', include(router.urls)),
    path('quotations/<int:pk>/send-email/', views.send_quotation_email, name='send-quotation-email'),
]
