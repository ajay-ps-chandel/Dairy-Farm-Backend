from django.contrib import admin
from .models import (
    MilkProductionLog, DailyProductionSummary,
    AnimalProductionSummary, MilkSale
)


@admin.register(MilkProductionLog)
class MilkProductionLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for MilkProductionLog model.
    """
    
    list_display = [
        'animal', 'date', 'session', 'quantity',
        'quality', 'fat_percentage', 'total_value', 'recorded_by'
    ]
    list_filter = ['session', 'quality', 'date', 'farm']
    search_fields = ['animal__tag_number', 'notes']
    list_select_related = ['animal', 'farm', 'recorded_by']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('animal', 'farm', 'date', 'session')
        }),
        ('Production', {
            'fields': ('quantity', 'quality', 'price_per_liter', 'total_value')
        }),
        ('Quality Metrics', {
            'fields': ('fat_percentage', 'snf_percentage', 'protein_percentage', 'lactose_percentage', 'temperature')
        }),
        ('Other', {
            'fields': ('notes', 'recorded_by')
        }),
    )
    
    readonly_fields = ['total_value']


@admin.register(DailyProductionSummary)
class DailyProductionSummaryAdmin(admin.ModelAdmin):
    """
    Admin configuration for DailyProductionSummary model.
    """
    
    list_display = [
        'farm', 'date', 'total_quantity', 'total_animals_milked',
        'average_fat', 'total_value'
    ]
    list_filter = ['date', 'farm']
    search_fields = ['farm__name']
    list_select_related = ['farm']
    date_hierarchy = 'date'
    
    readonly_fields = [
        'total_quantity', 'total_animals_milked', 'average_quantity_per_animal',
        'morning_quantity', 'afternoon_quantity', 'evening_quantity',
        'average_fat', 'average_snf', 'total_value', 'average_price_per_liter'
    ]


@admin.register(AnimalProductionSummary)
class AnimalProductionSummaryAdmin(admin.ModelAdmin):
    """
    Admin configuration for AnimalProductionSummary model.
    """
    
    list_display = [
        'animal', 'period_start', 'period_end', 'period_type',
        'total_quantity', 'average_per_day', 'total_value'
    ]
    list_filter = ['period_type', 'farm']
    search_fields = ['animal__tag_number']
    list_select_related = ['animal', 'farm']


@admin.register(MilkSale)
class MilkSaleAdmin(admin.ModelAdmin):
    """
    Admin configuration for MilkSale model.
    """
    
    list_display = [
        'buyer_name', 'date', 'quantity', 'total_amount',
        'payment_status', 'farm', 'recorded_by'
    ]
    list_filter = ['sale_type', 'payment_status', 'date', 'farm']
    search_fields = ['buyer_name', 'buyer_contact']
    list_select_related = ['farm', 'recorded_by']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Sale Info', {
            'fields': ('farm', 'date', 'sale_type')
        }),
        ('Buyer Details', {
            'fields': ('buyer_name', 'buyer_contact', 'buyer_address')
        }),
        ('Quantity & Price', {
            'fields': ('quantity', 'price_per_liter', 'total_amount')
        }),
        ('Quality', {
            'fields': ('fat_percentage', 'snf_percentage')
        }),
        ('Payment', {
            'fields': ('payment_status', 'amount_paid', 'payment_date', 'payment_method')
        }),
        ('Other', {
            'fields': ('notes', 'recorded_by')
        }),
    )
    
    readonly_fields = ['total_amount']
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        for sale in queryset:
            sale.payment_status = 'paid'
            sale.amount_paid = sale.total_amount
            sale.save()
    mark_as_paid.short_description = 'Mark selected sales as paid'
