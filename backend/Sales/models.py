from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    inverter_type = models.CharField(max_length=50, choices=[('Pure Sine Wave', 'Pure Sine Wave'), ('Modified Sine Wave', 'Modified Sine Wave'), ('Square Wave', 'Square Wave')])
    power_rating = models.IntegerField(validators=[MinValueValidator(1)])  # in watts
    frequency = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    efficiency = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    surge_power = models.IntegerField(validators=[MinValueValidator(1)])  # in watts
    warranty_years = models.IntegerField(validators=[MinValueValidator(0)])
    input_voltage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    output_voltage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate name based on other fields
        self.name = f"{self.inverter_type} {self.power_rating}W {self.frequency}Hz"

        # Generate model number based on other fields
        self.model_number = f"INV-{self.inverter_type[:3].upper()}-{self.power_rating}-{int(self.frequency)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class RFQ(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rfqs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"RFQ #{self.pk} - {self.status}"

class RFQItem(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rfq_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.unit_price}"



class Quotation(models.Model):
    STATUS_CHOICES = [
        ('quotation', 'Quotation'),
        ('quotation_sent', 'Quotation Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='quotations')
    date = models.DateField()
    expiration_date = models.DateField()
    invoicing_and_shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_quotations')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quotation #{self.pk} for {self.customer.name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='quotation_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='quotation_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('in_Production', 'In Production'),
        ('Ready_for_delivery', 'Ready for delivery'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now, editable=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} for {self.customer.name}"

class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
