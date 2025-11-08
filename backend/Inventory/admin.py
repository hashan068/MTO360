from django.contrib import admin
from .models import Supplier, Component, PurchaseRequisition, PurchaseOrder, ReplenishTransaction, ConsumptionTransaction

# Custom admin class for Supplier model
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('is_active',)
    ordering = ('name',)
    list_per_page = 10 

# Custom admin class for Component model
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'quantity', 'reorder_level', 'unit_of_measure', 'supplier', 'cost')
    search_fields = ('name', 'description', 'unit_of_measure', 'supplier__name')
    list_filter = ('unit_of_measure', 'supplier')
    ordering = ('name',)
    list_per_page = 10

# Custom admin class for PurchaseRequisition model
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'component', 'quantity', 'status', 'created_at', 'updated_at')
    search_fields = ('component__name', 'notes')
    list_filter = ('status', 'created_at', 'updated_at')
    list_per_page = 10

# Custom admin class for PurchaseOrder model
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'status', 'created_at', 'updated_at')
    search_fields = ('creator__username', 'purchase_requisition__component__name', 'notes')
    list_filter = ('status', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 10

# Custom admin class for ReplenishTransaction model
class ReplenishTransactionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_user_display', 'timestamp')
    search_fields = ('component__name', 'user_id__username')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    list_per_page = 10

    @admin.display(description='user')
    def get_user_display(self, obj):
        return obj.user_id

# Custom admin class for ConsumptionTransaction model
class ConsumptionTransactionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'material_requisition_item', 'component_id', 'quantity', 'timestamp')
    search_fields = ('material_requisition_item__name', 'component_id__name', 'user_id__username')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    list_per_page = 10

# Register your models with the admin site
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(PurchaseRequisition, PurchaseRequisitionAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(ReplenishTransaction, ReplenishTransactionAdmin)
admin.site.register(ConsumptionTransaction, ConsumptionTransactionAdmin)
