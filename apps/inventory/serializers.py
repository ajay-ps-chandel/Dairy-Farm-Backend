from rest_framework import serializers
from .models import (
    InventoryCategory, InventoryItem, StockTransaction,
    FeedFormula, FeedFormulaIngredient, InventoryAlert
)


class InventoryCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for inventory categories.
    """
    
    class Meta:
        model = InventoryCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class InventoryItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing inventory items.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'code', 'description',
            'category', 'category_name', 'item_type', 'item_type_display',
            'farm', 'farm_name', 'unit', 'unit_display',
            'quantity', 'reorder_level', 'max_stock',
            'stock_status', 'stock_value', 'needs_reorder',
            'unit_cost', 'supplier_name', 'is_active'
        ]

