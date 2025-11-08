from rest_framework import serializers
from .models import Customer, Product, RFQ, RFQItem, SalesOrder, SalesOrderItem, Quotation, QuotationItem
from Manufacturing.models import BillOfMaterial
from Manufacturing.serializers import BillOfMaterialSerializer
from decimal import Decimal

class ProductSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    bom = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'description', 'price', 'inverter_type',
            'power_rating', 'frequency', 'efficiency', 'surge_power',
            'warranty_years', 'input_voltage', 'output_voltage',
            'created_at', 'updated_at', 'bom'
        ]
        extra_kwargs = {
            'name': {'read_only': True},  # Exclude the name field from validation
        }

    def get_product_name(self, obj):
        return obj.name

    def get_bom(self, obj):
        try:
            bom_instance = obj.bill_of_material.first()  # Retrieve the first instance of BillOfMaterial
        except BillOfMaterial.DoesNotExist:
            return "Not Available"

        if bom_instance:
            bom_id = bom_instance.id  # Get the ID of the BOM
            return bom_id
        else:
            return "Not Available"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class RFQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQItem
        fields = ('id', 'rfq', 'product', 'quantity', 'unit_price')

class RFQSerializer(serializers.ModelSerializer):
    items = RFQItemSerializer(many=True, read_only=True)

    class Meta:
        model = RFQ
        fields = ('id', 'creator', 'created_at', 'updated_at', 'status', 'due_date', 'description', 'items')

class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['product', 'quantity', 'unit_price']

class QuotationSerializer(serializers.ModelSerializer):
    quotation_items = QuotationItemSerializer(many=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    date = serializers.DateField(format='%Y-%m-%d')
    expiration_date = serializers.DateField(format='%Y-%m-%d')
    # created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Quotation
        fields = ['id', 'customer', 'customer_name', 'date', 'expiration_date', 'invoicing_and_shipping_address', 'total_amount', 'status', 'quotation_items', 'created_by']

    def create(self, validated_data):
        quotation_items_data = validated_data.pop('quotation_items')
        total_amount = sum(item['quantity'] * item['unit_price'] for item in quotation_items_data)
        validated_data['total_amount'] = total_amount

        quotation = Quotation.objects.create(**validated_data)
        for quotation_item_data in quotation_items_data:
            QuotationItem.objects.create(quotation=quotation, **quotation_item_data)
        return quotation


class SalesOrderItemSerializer(serializers.ModelSerializer):
    sales_order_item_id = serializers.IntegerField(source='id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = ['sales_order_item_id', 'product', 'product_name', 'quantity', 'price']

class SalesOrderSerializer(serializers.ModelSerializer):
    order_items = SalesOrderItemSerializer(many=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_at_date = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrder
        fields = ['id', 'customer', 'customer_name', 'order_items', 'total_amount', 'status', 'created_at_date', 'updated_at']
    
    def get_created_at_date(self, obj):
        return obj.created_at.date()

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')

        total_amount = sum(Decimal(item['price']) * item['quantity'] for item in order_items_data)
        validated_data['total_amount'] = total_amount

        sales_order = SalesOrder.objects.create(**validated_data)

        for order_item_data in order_items_data:
            SalesOrderItem.objects.create(order=sales_order, **order_item_data)

        return sales_order
