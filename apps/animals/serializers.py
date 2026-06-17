from rest_framework import serializers
from .models import (
    Animal, AnimalHealthRecord, AnimalWeightLog,
    BreedingRecord, CalvingRecord, AnimalNote
)


class AnimalSerializer(serializers.ModelSerializer):
    """Serializer for listing  animals (minimal fields).
    """
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    breed_display = serializers.CharField(source='get_breed_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age = serializers.DictField(read_only = True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = Animal
        fields = [
            'id', 'tag_number', 'name', 'species', 'species_display',
            'breed', 'breed_display', 'gender', 'status', 'status_display',
            'farm', 'farm_name', 'age', 'is_pregnant', 'lactation_number',
            'image', 'is_active'
        ]
    

class AnimalDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for animal details
    """
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    breed_display = serializers.CharField(source='get_breed_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age = serializers.DictField(read_only=True)
    age_in_days = serializers.IntegerField(read_only=True)
    is_adult = serializers.BooleanField(read_only=True)
    current_lactation_days = serializers.IntegerField(read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    mother_tag = serializers.CharField(source='mother.tag_number', read_only=True)
    father_tag = serializers.CharField(source='father.tag_number', read_only=True)
    
    class Meta:
        model = Animal
        fields = [
            'id', 'tag_number', 'name', 'species', 'species_display',
            'breed', 'breed_display', 'gender', 'status', 'status_display',
            'farm', 'farm_name', 'date_of_birth', 'age', 'age_in_days',
            'is_adult', 'birth_weight', 'birth_location',
            'mother', 'mother_tag', 'father', 'father_tag',
            'color', 'current_weight', 'height',
            'lactation_number', 'last_calving_date',
            'expected_calving_date', 'is_pregnant',
            'current_lactation_days',
            'is_purchased', 'purchase_date', 'purchase_price', 'purchase_from',
            'is_sold', 'sale_date', 'sale_price', 'sale_to',
            'image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
class AnimalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating animals.
    """
    
    class Meta:
        model = Animal
        fields = [
            'tag_number', 'name', 'species', 'breed', 'gender',
            'farm', 'date_of_birth', 'birth_weight', 'birth_location',
            'mother', 'father', 'color', 'current_weight', 'height',
            'status', 'is_purchased', 'purchase_date',
            'purchase_price', 'purchase_from', 'image'
        ]
    
    def validate_tag_number(self, value):
        if Animal.objects.filter(tag_number=value).exists():
            raise serializers.ValidationError('Tag number already exists.')
        return value


class AnimalUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating animals.
    """
    
    class Meta:
        model = Animal
        fields = [
            'name', 'status', 'color', 'current_weight', 'height',
            'is_pregnant', 'expected_calving_date',
            'image', 'is_active'
        ]
        
    
    