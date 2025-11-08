# views.py for the Manufacturing app
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ManufacturingOrder, MaterialRequisition, BillOfMaterial, BOMItem
from .serializers import ManufacturingOrderSerializer, MaterialRequisitionSerializer, BillOfMaterialSerializer, BOMItemSerializer
from Sales.models import SalesOrderItem
from Inventory.models import Component
from .utils import get_bom_id_for_product
from rest_framework.decorators import action
from Inventory.models import ConsumptionTransaction

class MaterialRequisitionViewSet(viewsets.ModelViewSet):
    queryset = MaterialRequisition.objects.all()
    serializer_class = MaterialRequisitionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        current_user = request.user
        print (current_user.id)
        if serializer.is_valid():
            material_requisition = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillOfMaterialViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterial.objects.all()
    serializer_class = BillOfMaterialSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            bom = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BOMItemViewSet(viewsets.ModelViewSet):
    queryset = BOMItem.objects.all()
    serializer_class = BOMItemSerializer


class ManufacturingOrderViewSet(viewsets.ModelViewSet):
    queryset = ManufacturingOrder.objects.all()
    serializer_class = ManufacturingOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product_id = request.data.get('product_id')
            bom_id = get_bom_id_for_product(product_id)       
            
            if bom_id:
                validated_data = serializer.validated_data
                validated_data['bom_id'] = bom_id
                
                manufacturing_order = ManufacturingOrder.objects.create(**validated_data)
                return Response(ManufacturingOrderSerializer(manufacturing_order).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "No BOM found for the given product"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      