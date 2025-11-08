# Serializers for Manufacturing app
from rest_framework import serializers
from .models import ManufacturingOrder, MaterialRequisition,MaterialRequisitionItem, BillOfMaterial, BOMItem
from Inventory.models import Component, Supplier, PurchaseRequisition, PurchaseOrder
from Sales.models import SalesOrderItem
from Inventory.serializers import ComponentSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction

class MaterialRequisitionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialRequisitionItem
        fields = ['id', 'component', 'quantity', 'status']

class MaterialRequisitionSerializer(serializers.ModelSerializer):
    items = MaterialRequisitionItemSerializer(many=True, read_only=True)
    created_at_date = serializers.SerializerMethodField()

    class Meta:
        model = MaterialRequisition
        fields = ['id', 'manufacturing_order', 'bom', 'status', 'created_at', 'updated_at','created_at_date', 'items']
    
    def get_created_at_date(self, obj):
        return obj.created_at.date()

    @transaction.atomic
    def create(self, validated_data):
        manufacturing_order = validated_data['manufacturing_order']
        bom = validated_data.get('bom')

        material_requisition = MaterialRequisition.objects.create(**validated_data)
        items_data = []

        if bom:
            for bom_item in bom.bom_items.all():
                quantity = manufacturing_order.quantity * bom_item.quantity
                item_data = {
                    'material_requisition': material_requisition,
                    'component': bom_item.component,
                    'quantity': quantity
                }
                items_data.append(item_data)
                MaterialRequisitionItem.objects.create(**item_data)

        # Update the manufacturing order status to 'mr_sent'
        manufacturing_order.update_status('mr_sent')
        
        return material_requisition


class BOMItemSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='component.name', read_only=True)
    class Meta:
        model = BOMItem
        fields = ['id', 'bill_of_material', 'component','component_name', 'quantity']
        read_only_fields = ['bill_of_material']


class BillOfMaterialSerializer(serializers.ModelSerializer):
    bom_items = BOMItemSerializer(many=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = BillOfMaterial
        fields = ('id', 'name', 'product', 'product_name', 'bom_items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        bom_items_data = validated_data.pop('bom_items', [])
        bill_of_material = BillOfMaterial.objects.create(**validated_data)

        for bom_item_data in bom_items_data:
            BOMItem.objects.create(bill_of_material=bill_of_material, **bom_item_data)

        return bill_of_material


class ManufacturingOrderSerializer(serializers.ModelSerializer):
    sales_order_item = serializers.PrimaryKeyRelatedField(queryset=SalesOrderItem.objects.all(), required=False, allow_null=True)
    sales_order = serializers.PrimaryKeyRelatedField(queryset=SalesOrderItem.objects.all(), source='sales_order_item', required=False, allow_null=True)
    created_at_date = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    
    class Meta:
        model = ManufacturingOrder
        fields = [
            'id','sales_order', 'product_id','product_name', 'quantity', 'bom', 'status', 'created_at',
            'updated_at', 'end_at', 'production_start_at',
            'estimated_mfg_lead_time', 'mfg_lead_time', 'production_lead_time',
            'sales_order_item', 'creater', 'created_at_date'
        ]
        read_only_fields = [
            'created_at', 'updated_at',
            'end_at', 'production_start_at', 'mfg_lead_time', 'production_lead_time'
        ]    
    
    def get_created_at_date(self, obj):
        return obj.created_at.date()

    def create(self, validated_data):
        print(f"Validated data: {validated_data}")
        return ManufacturingOrder.objects.create(**validated_data)
