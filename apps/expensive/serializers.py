from rest_framework import serializers
from .models import ExpenseCategory, Expense, RecurringExpense, ExpenseBudget


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for expense categories.
    """
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'category_type', 'category_type_display', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExpenseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing expenses.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'farm', 'farm_name',
            'category', 'category_name', 'amount', 'tax_amount', 'total_amount',
            'expense_date', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'vendor_name',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for expense details.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    related_animal_tag = serializers.CharField(source='related_animal.tag_number', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'farm', 'farm_name',
            'category', 'category_name', 'amount', 'tax_amount', 'total_amount',
            'expense_date', 'payment_method', 'payment_method_display',
            'payment_reference', 'vendor_name', 'vendor_contact',
            'status', 'status_display', 'invoice_number', 'receipt',
            'related_animal', 'related_animal_tag',
            'approved_by', 'approved_by_name', 'approved_at',
            'notes', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating expenses.
    """
    
    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'farm', 'category',
            'amount', 'tax_amount', 'expense_date',
            'payment_method', 'payment_reference',
            'vendor_name', 'vendor_contact',
            'invoice_number', 'receipt',
            'related_animal', 'notes'
        ]
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class RecurringExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for recurring expenses.
    """
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = RecurringExpense
        fields = [
            'id', 'title', 'description', 'farm', 'farm_name',
            'category', 'category_name', 'amount', 'frequency', 'frequency_display',
            'start_date', 'end_date', 'next_due_date',
            'vendor_name', 'is_active',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseBudgetSerializer(serializers.ModelSerializer):
    """
    Serializer for expense budgets.
    """
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    utilization_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ExpenseBudget
        fields = [
            'id', 'farm', 'farm_name', 'category', 'category_name',
            'period', 'period_display', 'period_start', 'period_end',
            'budget_amount', 'spent_amount', 'remaining_amount',
            'utilization_percentage', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseStatsSerializer(serializers.Serializer):
    """
    Serializer for expense statistics.
    """
    total_expenses_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses_this_week = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses_this_year = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses_by_category = serializers.ListField(child=serializers.DictField())
    expenses_by_payment_method = serializers.ListField(child=serializers.DictField())
    pending_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    top_vendors = serializers.ListField(child=serializers.DictField())


class BudgetComparisonSerializer(serializers.Serializer):
    """
    Serializer for budget comparison.
    """
    budget_id = serializers.IntegerField()
    category_name = serializers.CharField()
    budget_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    utilization_percentage = serializers.FloatField()
    status = serializers.CharField()
