# Inventory app models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from Notifications.models import Notification
# from django.utils.text import slugify
# import uuid
from django.db.models import SET_DEFAULT, SET_NULL

# User = get_user_model()

# def get_default_user():
#     return User.objects.filter(is_superuser=True).first()

# superuser = get_default_user()
# superuser_pk = superuser.pk if superuser else 1
User = get_user_model()

def get_default_user():
    # Lazy evaluation: Return a function to be called when needed
    return User.objects.filter(is_superuser=True).first()
    
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(default=None)
    address = models.TextField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Suppliers'
        
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Component(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # sku = models.CharField(max_length=100, unique=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=SET_NULL, null=True, blank=True, related_name='components')
    reorder_level = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)
    order_quantity = models.PositiveIntegerField(default=0)
    unit_of_measure = models.CharField(max_length=20, default='pcs')
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)
        self.check_inventory()

    def check_inventory(self):
        if self.quantity < self.reorder_level and self.order_quantity == 0:
            purchase_requisition = PurchaseRequisition.objects.create(component=self, quantity=self.reorder_quantity, priority='high', status='pending')
            self.order_quantity = self.reorder_quantity
            self.notify_low_inventory()
            
            

    def notify_low_inventory(self):
        user = get_default_user()
        Notification.objects.create(
            user=user,
            message=f"Inventory level for {self.name} is below the reorder level."
    )


class PurchaseRequisition(models.Model):
    # Define choices for status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
        ('fulfilled', _('Fulfilled')),
    ]

    # Define choices for priority
    PRIORITY_CHOICES = [
        ('high', _('High')),
        ('medium', _('Medium')),
        ('low', _('Low')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expected_delivery_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='high')

    class Meta:
        ordering = ['-created_at']
        # ordering = ['priority', 'status']

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('open_order', _('Open Order')),
        ('approved', _('Approved')),
        ('received', _('Received')),
        ('invoiced', _('Invoiced')),
        ('cancelled', _('Cancelled')),
        ('rejected', _('Rejected')),
    ]

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None)
    
    purchase_requisition = models.ForeignKey('PurchaseRequisition', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2,blank=True,)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, editable=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Purchase Order #{self.id} - {self.purchase_requisition.component} - {self.purchase_requisition.quantity} units"

    def save(self, *args, **kwargs):
        self.total_price = self.purchase_requisition.quantity * self.price_per_unit
        super().save(*args, **kwargs)

class ReplenishTransaction(models.Model): 
    purchase_requisition = models.ForeignKey('PurchaseRequisition', on_delete=models.CASCADE)
    component = models.ForeignKey('Component', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Replenish of {self.quantity} {self.component} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Update the quantity of the associated Component
        self.component.quantity += self.quantity
        self.component.save()

        # Call the save method of the parent class
        super().save(*args, **kwargs)

class ConsumptionTransaction(models.Model):
    material_requisition_item = models.ForeignKey('Manufacturing.MaterialRequisitionItem', on_delete=models.CASCADE)
    component_id = models.ForeignKey('Inventory.Component', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)


    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Consumption of {self.quantity} {self.component_id.name} at {self.timestamp}"
