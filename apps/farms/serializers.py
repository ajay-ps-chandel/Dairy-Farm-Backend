from rest_framework import serializers
from .models import Farm, FarmDocument, FarmNote, FarmSettings


class FarmSettingsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FarmSettings
        fields = [
            'id', 'milking_sessions_per_day', 'default_milk_price',
            'low_inventory_threshold', 'animal_health_alert_days',
            'email_notifications', 'sms_notifications',
            'currency', 'weight_unit', 'volume_unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class FarmListSerializer(serializers.ModelSerializer):
    
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    farm_type_display = serializers.CharField(source='get_farm_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    capacity_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'code', 'farm_type', 'farm_type_display',
            'status', 'status_display', 'owner', 'owner_name',
            'city', 'state', 'current_animals', 'max_animals',
            'capacity_percentage', 'created_at'
        ]
        
class FarmDetailSerializer(serializers.ModelSerializer):
    
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    farm_type_display = serializers.CharField(source='get_farm_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    capacity_percentage = serializers.FloatField(read_only=True)
    available_capacity = serializers.IntegerField(read_only=True)
    settings = FarmSettingsSerializer(read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'code', 'description', 'farm_type',
            'farm_type_display', 'status', 'status_display',
            'owner', 'owner_name', 'city', 'state',
            'current_animals', 'max_animals',
            'capacity_percentage', 'available_capacity',
            'settings', 'created_at'
        ]
        
class FarmCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Farm
        fields = [
            'name', 'description', 'farm_type', 'address',
            'city', 'state', 'country', 'pincode',
            'latitude', 'longitude', 'contact_person',
            'contact_phone', 'contact_email', 'total_area',
            'grazing_area', 'built_up_area', 'max_animals',
            'has_milking_parlor', 'has_cold_storage',
            'has_veterinary_facility', 'has_feed_storage'
        ]
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        farm = Farm.objects.create(**validated_data)
        FarmSettings.objects.create(farm=farm)  
        return farm
    
class FarmUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Farm
        fields = [
            'name', 'description', 'farm_type', 'status',
            'address', 'city', 'state', 'pincode',
            'latitude', 'longitude', 'contact_person',
            'contact_phone', 'contact_email', 'total_area',
            'grazing_area', 'built_up_area', 'max_animals',
            'has_milking_parlor', 'has_cold_storage',
            'has_veterinary_facility', 'has_feed_storage',
            'is_active'
        ]
        
class FarmDocumentSerializer(serializers.ModelSerializer):
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = FarmDocument
        fields = [
            'id', 'farm', 'farm_name', 'document_type',
            'document_type_display', 'title', 'file',
            'description', 'issue_date', 'expiry_date',
            'document_number', 'is_verified', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
        
class FarmNoteSerializer(serializers.ModelSerializer):
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = FarmNote
        fields = [
            'id', 'farm', 'farm_name', 'title', 'content',
            'created_by', 'created_by_name', 'is_important',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
class FarmStatsSerializer(serializers.ModelSerializer):
    
    total_farms = serializers.IntegerField()
    active_farms = serializers.IntegerField()
    total_animals = serializers.IntegerField()
    total_capacity = serializers.IntegerField()
    capacity_utilization = serializers.FloatField()
    farms_by_type = serializers.DictField(child=serializers.IntegerField())
    farms_by_status = serializers.DictField(child=serializers.IntegerField())
    