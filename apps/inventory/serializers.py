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


class InventoryItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for inventory item details.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'code', 'description',
            'category', 'category_name', 'item_type', 'item_type_display',
            'farm', 'farm_name', 'unit', 'unit_display',
            'quantity', 'reorder_level', 'max_stock',
            'stock_status', 'stock_value', 'needs_reorder',
            'unit_cost', 'supplier_name', 'supplier_contact',
            'is_active', 'recent_transactions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_recent_transactions(self, obj):
        transactions = obj.transactions.all()[:10]
        return StockTransactionSerializer(transactions, many=True).data


class InventoryItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating inventory items.
    """
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'category', 'item_type',
            'farm', 'unit', 'quantity', 'reorder_level',
            'max_stock', 'unit_cost', 'supplier_name', 'supplier_contact'
        ]


class StockTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for stock transactions.
    """
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = [
            'id', 'item', 'item_name', 'item_code',
            'transaction_type', 'transaction_type_display',
            'date', 'quantity', 'unit_cost', 'total_cost',
            'supplier_name', 'invoice_number', 'reference',
            'notes', 'balance_after',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'total_cost', 'balance_after', 'created_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

