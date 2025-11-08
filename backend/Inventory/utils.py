# utils.py
from django.db import transaction

from .models import ConsumptionTransaction, Component

from django.shortcuts import get_object_or_404

def get_material_requisition_serializer():
    from Manufacturing.serializers import MaterialRequisitionSerializer
    return MaterialRequisitionSerializer

def get_manufacturing_order_serializer():
    from Manufacturing.serializers import ManufacturingOrderSerializer
    return ManufacturingOrderSerializer

def get_material_requisition_item_serializer():
    from Manufacturing.serializers import MaterialRequisitionItemSerializer
    return MaterialRequisitionItemSerializer

def update_component_quantity(component_id, quantity):
    component = get_object_or_404(Component, id=component_id)
    if component.quantity < quantity:
        raise Exception(f"Insufficient quantity for component {component.name}. Available quantity: {component.quantity}")
    component.quantity -= quantity  # Reduce the component quantity by the consumed amount
    component.save()
    

# update material_requisition item status
def update_material_requisition_item_status(material_requisition_item):
    MaterialRequisitionItemSerializer = get_material_requisition_item_serializer()
    serializer = MaterialRequisitionItemSerializer(material_requisition_item, data={'status': 'approved'}, partial=True)

    if serializer.is_valid():
        serializer.save()
        print(f"MaterialRequisitionItem status updated to approved")
    else:
        raise Exception(f"Failed to update MaterialRequisitionItem status: {serializer.errors}")


def update_material_requisition_status(material_requisition):
    MaterialRequisitionSerializer = get_material_requisition_serializer()
    serializer = MaterialRequisitionSerializer(material_requisition, data={'status': 'approved'}, partial=True)

    if serializer.is_valid():
        serializer.save()
    else:
        raise Exception(f"Failed to update MaterialRequisition status: {serializer.errors}")


def update_manufacturing_order_status(manufacturing_order):
    ManufacturingOrderSerializer = get_manufacturing_order_serializer()
    serializer = ManufacturingOrderSerializer(manufacturing_order, data={'status': 'mr_approved'}, partial=True)

    if serializer.is_valid():
        serializer.save()
    else:
        raise Exception(f"Failed to update Manaufacturing Order status: {serializer.errors}")