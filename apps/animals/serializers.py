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
        
    
class AnimalHealthRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for animal health records.
    """
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalHealthRecord
        fields = [
            'id', 'animal', 'animal_tag', 'record_type', 'record_type_display',
            'date', 'description', 'symptoms', 'diagnosis', 'treatment',
            'medications', 'dosage', 'veterinarian_name', 'veterinarian_contact',
            'cost', 'follow_up_date', 'follow_up_notes', 'documents',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
class AnimalWeightLogSerializer(serializers.ModelSerializer):
    """
    Serializer for animal weight logs.
    """
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalWeightLog
        fields = [
            'id', 'animal', 'animal_tag', 'date', 'weight',
            'notes', 'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
class BreedingRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for breeding records.
    """
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    female_tag = serializers.CharField(source='female.tag_number', read_only=True)
    male_tag = serializers.CharField(source='male.tag_number', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = BreedingRecord
        fields = [
            'id', 'female', 'female_tag', 'male', 'male_tag',
            'breeding_date', 'method', 'method_display',
            'semen_source', 'semen_batch', 'inseminator_name',
            'status', 'status_display', 'pregnancy_check_date',
            'expected_calving_date', 'actual_calving_date',
            'calving_notes', 'farm', 'farm_name',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
class CalvingRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for calving records.
    """
    calving_type_display = serializers.CharField(source='get_calving_type_display', read_only=True)
    calf_gender_display = serializers.CharField(source='get_calf_gender_display', read_only=True)
    mother_tag = serializers.CharField(source='mother.tag_number', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = CalvingRecord
        fields = [
            'id', 'mother', 'mother_tag', 'breeding',
            'calving_date', 'calving_type', 'calving_type_display',
            'calf_tag_number', 'calf_gender', 'calf_gender_display',
            'calf_weight', 'calf_health_status',
            'complications', 'treatment_given', 'assisted_by',
            'farm', 'farm_name', 'recorded_by', 'recorded_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'recorded_by']
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class AnimalNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for animal notes.
    """
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = AnimalNote
        fields = [
            'id', 'animal', 'animal_tag', 'title', 'content',
            'is_important', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
class AnimalStatsSerializer(serializers.Serializer):
    """
    Serializer for animal statistics.
    """
    total_animals = serializers.IntegerField()
    by_species = serializers.DictField(child=serializers.IntegerField())
    by_breed = serializers.DictField(child=serializers.IntegerField())
    by_status = serializers.DictField(child=serializers.IntegerField())
    by_gender = serializers.DictField(child=serializers.IntegerField())
    pregnant_count = serializers.IntegerField()
    lactating_count = serializers.IntegerField()
    adult_count = serializers.IntegerField()
    calf_count = serializers.IntegerField()
    recent_additions = serializers.IntegerField()
    recent_sales = serializers.IntegerField()
    
    
class AnimalPedigreeSerializer(serializers.ModelSerializer):
    """
    Serializer for animal pedigree information.
    """
    age = serializers.DictField(read_only=True)
    offspring = serializers.SerializerMethodField()
    
    class Meta:
        model = Animal
        fields = [
            'id', 'tag_number', 'name', 'species', 'breed',
            'gender', 'date_of_birth', 'age',
            'mother', 'father', 'offspring'
        ]
    
    def get_offspring(self, obj):
        if obj.gender == 'female':
            offspring = obj.offspring_as_mother.all()
        else:
            offspring = obj.offspring_as_father.all()
        return [
            {
                'id': child.id,
                'tag_number': child.tag_number,
                'name': child.name,
                'gender': child.gender,
                'date_of_birth': child.date_of_birth
            }
            for child in offspring[:10]
        ]