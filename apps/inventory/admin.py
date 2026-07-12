from django.contrib import admin
from .models import (
    InventoryCategory, InventoryItem, StockTransaction
)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for InventoryCategory model.
    """
    
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for InventoryItem model.
    """
    
    list_display = [
        'name', 'code', 'item_type', 'farm',
        'quantity', 'reorder_level', 'unit_cost', 'is_active'
    ]
    list_filter = ['item_type', 'is_active', 'category', 'farm']
    search_fields = ['name', 'code', 'description']
    list_select_related = ['category', 'farm']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'code', 'description', 'category', 'item_type')
        }),
        ('Farm', {
            'fields': ('farm',)
        }),
        ('Unit & Stock', {
            'fields': ('unit', 'quantity', 'reorder_level', 'max_stock')
        }),
        ('Pricing', {
            'fields': ('unit_cost',)
        }),
        ('Supplier', {
            'fields': ('supplier_name', 'supplier_contact')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['code']
    
    actions = ['activate_items', 'deactivate_items']
    
    def activate_items(self, request, queryset):
        queryset.update(is_active=True)
    activate_items.short_description = 'Activate selected items'
    
    def deactivate_items(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_items.short_description = 'Deactivate selected items'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for StockTransaction model.
    """
    
    list_display = [
        'item', 'transaction_type', 'date',
        'quantity', 'total_cost', 'recorded_by'
    ]
    list_filter = ['transaction_type', 'date']
    search_fields = ['item__name', 'reference', 'notes']
    list_select_related = ['item', 'recorded_by']
    date_hierarchy = 'date'
    
    readonly_fields = ['total_cost', 'balance_after']


      