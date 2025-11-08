from django.contrib import admin
from .models import ManufacturingOrder, MaterialRequisition, BillOfMaterial, BOMItem, MaterialRequisitionItem

# Register your models here.

class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 0
    list_per_page = 10

class MaterialRequisitionItemInline(admin.TabularInline):
    model = MaterialRequisitionItem
    extra = 0
    list_per_page = 10

class MaterialRequisitionAdmin(admin.ModelAdmin):
    inlines = [MaterialRequisitionItemInline]
    list_display = ('id', 'manufacturing_order', 'bom', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('manufacturing_order__id',)
    list_per_page = 10

class BillOfMaterialAdmin(admin.ModelAdmin):
    inlines = [BOMItemInline]
    list_display = ('name', 'product', 'created_at', 'updated_at')
    search_fields = ('name', 'product__name')
    list_per_page = 10

admin.site.register(ManufacturingOrder)
admin.site.register(MaterialRequisition, MaterialRequisitionAdmin)
admin.site.register(BillOfMaterial, BillOfMaterialAdmin)
admin.site.register(BOMItem)
