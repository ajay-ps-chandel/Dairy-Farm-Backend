from django.contrib import admin
from .models import (
    Animal, AnimalHealthRecord, AnimalWeightLog,
    BreedingRecord, CalvingRecord, AnimalNote
)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    """Admin configuration for Animal model.
    """
    
    list_display = [
        'tag_number', 'name', 'species', 'breed', 'gender',
        'farm', 'status', 'is_pregnant', 'lactation_number', 'is_active'
    ]
    list_filter = [
        'species', 'breed', 'gender', 'status', 'is_pregnant',
        'is_active', 'farm', 'date_of_birth'
    ]
    search_fields = ['tag_number', 'name', 'farm__name']
    list_select_related = ['farm', 'mother', 'father']
    date_hierarchy = 'date_of_birth'
    fieldsets = (
        ('Identification', {
            'fields': ('tag_number', 'name', 'species', 'breed', 'gender')
        }),
        ('Farm', {
            'fields': ('farm',)
        }),
        ('Birth Details', {
            'fields': ('date_of_birth', 'birth_weight', 'birth_location')
        }),
        ('Parentage', {
            'fields': ('mother', 'father')
        }),
        ('Physical Characteristics', {
            'fields': ('color', 'current_weight', 'height')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_pregnant', 'lactation_number')
        }),
        ('Calving', {
            'fields': ('last_calving_date', 'expected_calving_date')
        }),
        ('Purchase', {
            'fields': ('is_purchased', 'purchase_date', 'purchase_price', 'purchase_from')
        }),
        ('Sale', {
            'fields': ('is_sold', 'sale_date', 'sale_price', 'sale_to')
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )
    
    actions = ['activate_animals', 'deactivate_animals', 'mark_as_lactating']
    
    def activate_animals(self, request, queryset):
        queryset.update(is_active=True)
    activate_animals.short_description = 'Activate selected animals'
    
    def deactivate_animals(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_animals.short_description = 'Deactivate selected animals'
    
    def mark_as_lactating(self, request, queryset):
        queryset.filter(gender='female').update(status='lactating')
    mark_as_lactating.short_description = 'Mark selected females as lactating'


@admin.register(AnimalHealthRecord)
class AnimalHealthRecordAdmin(admin.ModelAdmin):
    """Admin configuration for AnimalHealthRecord model.
    """
    
    list_display = ['animal', 'record_type', 'date', 'veterinarian_name', 'cost']
    list_filter = [ 'record_type','date']
    search_fields = ['animal__tag_number', 'description']
    date_hierarchy = 'date'
    
@admin.register(AnimalWeightLog)
class AnimalWeightLogAdmin(admin.ModelAdmin):
    """Admin configuration for AnimalWeightLog model.
    """
    
    list_display = ['animal', 'date', 'weight', 'recorded_by']
    list_filter = ['date']
    search_fields = ['animal__tag_number']
    list_select_related = ['animal', 'recorded_by']
    date_hierarchy = 'date'
    

@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    """
    Admin configuration for BreedingRecord model.
    """
    
    list_display = [
        'female', 'male', 'breeding_date', 'method', 'status', 'farm'
    ]
    list_filter = ['method', 'status', 'breeding_date']
    search_fields = ['female__tag_number', 'male__tag_number']
    list_select_related = ['female', 'male', 'farm']
    date_hierarchy = 'breeding_date'