from datetime import datetime
import random
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Customer, Product, RFQ, RFQItem, SalesOrder, SalesOrderItem, Quotation, QuotationItem
from .serializers import CustomerSerializer, ProductSerializer,RFQSerializer, RFQItemSerializer, SalesOrderSerializer, SalesOrderItemSerializer, QuotationSerializer, QuotationItemSerializer
import requests
from django.http import JsonResponse
from django.conf import settings
from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.decorators import api_view
from datetime import timedelta
import requests
# from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def send_quotation_email(request, pk):
    try:
        quotation = Quotation.objects.get(pk=pk)
        print(f"Quotation instance: {quotation}")

        recipient_email = quotation.customer.email
        print(f"Recipient email: {recipient_email}")

        subject = f"Quotation #{quotation.id}"
        print(f"Subject: {subject}")

        text = f"Dear {quotation.customer.name},\n\nPlease find your quotation details below:\n\n{QuotationSerializer(quotation).data['quotation_items']}"
        print(f"Email text: {text}")

        response = requests.post(
            f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": f"Your Company <mailgun@{settings.MAILGUN_DOMAIN}>",
                "to": [recipient_email],
                "subject": subject,
                "text": text,
            },
        )
        print(requests.post)
        print(f"Mailgun response status code: {response.status_code}")
        print(f"Mailgun response content: {response.content}")

        if response.status_code == 200:
            return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Quotation.DoesNotExist:
        return Response({"error": "Quotation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Exception: {e}")

        return Response({"error": "An error occurred while sending the email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RFQItemViewSet(viewsets.ModelViewSet):
    queryset = RFQItem.objects.all()
    serializer_class = RFQItemSerializer

class RFQViewSet(viewsets.ModelViewSet):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer

class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            quotation = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesOrderItemViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = SalesOrder.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        elif start_date:
            queryset = queryset.filter(
                created_at__date__gte=start_date
            )
        elif end_date:
            queryset = queryset.filter(
                created_at__date__lte=end_date
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # random_date = datetime(2023, random.randint(1, 12), random.randint(1, 28))
            # serializer.validated_data['created_at'] = random_date
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
