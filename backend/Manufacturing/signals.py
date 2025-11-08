from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MaterialRequisitionItem, ManufacturingOrder

@receiver(post_save, sender=MaterialRequisitionItem)
def update_material_requisition_status(sender, instance, **kwargs):
    instance.material_requisition.update_status()
    manufacturing_order = instance.material_requisition.manufacturing_order
    update_manufacturing_order_status(manufacturing_order)

def get_manufacturing_order_serializer():
    from Manufacturing.serializers import ManufacturingOrderSerializer
    return ManufacturingOrderSerializer

def update_manufacturing_order_status(manufacturing_order):
    ManufacturingOrderSerializer = get_manufacturing_order_serializer()
    serializer = ManufacturingOrderSerializer(manufacturing_order, data={'status': 'mr_approved'}, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        raise Exception(f"Failed to update Manufacturing Order status: {serializer.errors}")



# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import MaterialRequisitionItem

# @receiver(post_save, sender=MaterialRequisitionItem)
# def update_material_requisition_status(sender, instance, **kwargs):
#     instance.material_requisition.update_status()

