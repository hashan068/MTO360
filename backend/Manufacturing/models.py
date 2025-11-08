# Manufacturing app models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from Inventory.models import Component
from Sales.models import SalesOrderItem, Product
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings

class ManufacturingOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('mr_sent', _('MR Sent')),
        ('mr_approved', _('MR Approved')),
        ('mr_rejected', _('MR Rejected')),
        ('in_production', _('In Production')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE, related_name='manufacturing_orders', null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='manufacturing_orders', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    bom = models.ForeignKey('BillOfMaterial', on_delete=models.CASCADE, related_name='manufacturing_orders', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    creater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    end_at = models.DateTimeField(null=True, blank=True)
    production_start_at = models.DateTimeField(null=True, blank=True)
    estimated_mfg_lead_time = models.DurationField(null=True, blank=True)
    mfg_lead_time = models.DurationField(null=True, blank=True)
    production_lead_time = models.DurationField(null=True, blank=True)

    def update_status(self, new_status):
        self.status = new_status
        if new_status == 'in_production':
            self.production_start_at = timezone.now()
        elif new_status == 'completed':
            now = timezone.now()
            self.mfg_lead_time = now - self.created_at
            if self.production_start_at:
                self.production_lead_time = now - self.production_start_at
            self.end_at = now
        self.save()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.sales_order_item:
            return f"Quotation #{self.pk}"
        else:
            return "Manufacturing Order with no associated Sales Order Item"


class MaterialRequisition(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),

        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('partialy_approved', _('Partially_Approved')),
        ('fulfilled', _('Fulfilled')),
    ]

    manufacturing_order = models.ForeignKey(ManufacturingOrder, on_delete=models.CASCADE, related_name='material_requisitions')
    bom = models.ForeignKey('BillOfMaterial', on_delete=models.CASCADE, related_name='material_requisitions', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_status(self):
        all_items = self.items.all()
        approved_items = all_items.filter(status='approved')

        if not all_items:
            self.status = 'pending'
        elif approved_items.count() == all_items.count():
            self.status = 'approved'
        elif approved_items.exists():
            self.status = 'partialy_approved'
        else:
            self.status = 'pending'

        self.save()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Material Requisition for {self.manufacturing_order}"


class MaterialRequisitionItem(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
    ]

    material_requisition = models.ForeignKey(MaterialRequisition, on_delete=models.CASCADE, related_name='items')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='material_requisition_items')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=MaterialRequisition.STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.quantity} x {self.component} for Material Requisition {self.material_requisition}"


class BillOfMaterial(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bill_of_material', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BOMItem(models.Model):
    bill_of_material = models.ForeignKey(BillOfMaterial, on_delete=models.CASCADE, related_name='bom_items')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='bom_items', null=True, default=1, blank=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.component}"

    class Meta:
        verbose_name = _('BOM Item')
