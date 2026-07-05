from django.contrib import admin
from .models import ExpenseCategory, Expense, RecurringExpense,ExpenseBudget

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExpenseCategory model.
    """
    
    list_display = ['name', 'category_type', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Expense model.
    """
    
    list_display = [
        'title', 'expense_date', 'amount', 'total_amount',
        'category', 'status', 'farm', 'recorded_by'
    ]
    list_filter = ['status', 'payment_method', 'expense_date', 'category', 'farm']
    search_fields = ['title', 'vendor_name', 'invoice_number']
    list_select_related = ['category', 'farm', 'recorded_by']
    date_hierarchy = 'expense_date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'farm', 'category')
        }),
        ('Amount', {
            'fields': ('amount', 'tax_amount', 'total_amount')
        }),
        ('Date & Payment', {
            'fields': ('expense_date', 'payment_method', 'payment_reference')
        }),
        ('Vendor', {
            'fields': ('vendor_name', 'vendor_contact')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
        ('Invoice', {
            'fields': ('invoice_number', 'receipt')
        }),
        ('Related', {
            'fields': ('related_animal',)
        }),
        ('Other', {
            'fields': ('notes', 'recorded_by')
        }),
    )
    
    readonly_fields = ['total_amount', 'approved_at']
    
    actions = ['approve_expenses', 'mark_as_paid']
    
    def approve_expenses(self, request, queryset):
        queryset.update(status='approved')
    approve_expenses.short_description = 'Approve selected expenses'
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = 'Mark selected expenses as paid'


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    """
    Admin configuration for RecurringExpense model.
    """
    
    list_display = [
        'title', 'amount', 'frequency', 'next_due_date',
        'farm', 'is_active'
    ]
    list_filter = ['frequency', 'is_active', 'farm']
    search_fields = ['title', 'vendor_name']
    list_select_related = ['farm']


@admin.register(ExpenseBudget)
class ExpenseBudgetAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExpenseBudget model.
    """
    
    list_display = [
        'farm', 'category', 'period', 'period_start',
        'budget_amount', 'created_at'
    ]
    list_filter = ['period', 'farm', 'category']
    search_fields = ['category__name']
    list_select_related = ['farm', 'category']
