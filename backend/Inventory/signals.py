# Inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequisition, PurchaseOrder
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=PurchaseRequisition)
def create_purchase_order(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        purchase_order = PurchaseOrder.objects.create(
            creator=User.objects.filter(is_superuser=True).first(),
            purchase_requisition=instance,
            supplier=instance.component.supplier,
            price_per_unit = instance.component.cost,
            status='draft'
        )
        print(f'Purchase Order {purchase_order.id} created for Requisition {instance.id}')