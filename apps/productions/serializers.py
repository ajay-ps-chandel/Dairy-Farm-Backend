
from rest_framework import serializers
from .models import (
    MilkProductionLog, DailyProductionSummary,
    AnimalProductionSummary, MilkSale
)
from animals.models import Animal
from farms.models import Farm

class MilkProductionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for milk production logs.
    """
    session_display = serializers.CharField(source='get_session_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = MilkProductionLog
        fields = [
            'id', 'animal', 'animal_tag', 'animal_name',
            'farm', 'farm_name', 'date', 'session', 'session_display',
            'quantity', 'quality', 'quality_display',
            'fat_percentage', 'snf_percentage', 'protein_percentage',
            'lactose_percentage', 'temperature',
            'price_per_liter', 'total_value', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_value', 'created_at', 'updated_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
class MilkProductionLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating milk production logs.
    """
    
    class Meta:
        model = MilkProductionLog
        fields = [
            'animal', 'farm', 'date', 'session',
            'quantity', 'quality', 'fat_percentage',
            'snf_percentage', 'protein_percentage',
            'lactose_percentage', 'temperature',
            'price_per_liter', 'notes'
        ]
    
    def validate(self, data):
        # Check if animal belongs to farm
        if data['animal'].farm != data['farm']:
            raise serializers.ValidationError("The selected animal does not belong to the specified farm.")
        
        # Check if the animal is female
        if data['animal'].gender != 'female':
            raise serializers.ValidationError("Milk production logs can only be created for female animals.")
        
        return data
    
    
class DailyProductionSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for daily production summaries.
    """
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = DailyProductionSummary
        fields = [
            'id', 'farm', 'farm_name', 'date',
            'total_quantity', 'total_animals_milked',
            'average_quantity_per_animal',
            'morning_quantity', 'afternoon_quantity', 'evening_quantity',
            'average_fat', 'average_snf',
            'total_value', 'average_price_per_liter',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
class AnimalProductionSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for animal production summaries.
    """
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = AnimalProductionSummary
        fields = [
            'id', 'animal', 'animal_tag', 'animal_name',
            'farm', 'farm_name', 'period_start', 'period_end',
            'period_type', 'total_quantity', 'total_sessions',
            'average_per_session', 'average_per_day',
            'peak_quantity', 'peak_date',
            'average_fat', 'average_snf', 'total_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
class MilkSaleSerializer(serializers.ModelSerializer):
    """
    Serializer for milk sales.
    """
    sale_type_display = serializers.CharField(source='get_sale_type_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = MilkSale
        fields = [
            'id', 'farm', 'farm_name', 'date', 'sale_type', 'sale_type_display',
            'buyer_name', 'buyer_contact', 'buyer_address',
            'quantity', 'price_per_liter', 'total_amount',
            'fat_percentage', 'snf_percentage',
            'payment_status', 'payment_status_display',
            'amount_paid', 'payment_date', 'payment_method',
            'balance_due', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class MilkSaleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating milk sales.
    """
    
    class Meta:
        model = MilkSale
        fields = [
            'buyer_name', 'buyer_contact', 'buyer_address',
            'quantity', 'price_per_liter',
            'fat_percentage', 'snf_percentage',
            'payment_status', 'amount_paid', 'payment_date',
            'payment_method', 'notes'
        ]


