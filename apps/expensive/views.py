from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import ExpenseCategory, Expense, RecurringExpense, ExpenseBudget
from .serializers import (
    ExpenseCategorySerializer,
    ExpenseListSerializer,
    ExpenseDetailSerializer,
    ExpenseCreateSerializer,
    RecurringExpenseSerializer,
    ExpenseBudgetSerializer,
    ExpenseStatsSerializer,
    BudgetComparisonSerializer,
)
from apps.accounts.permissions import IsFarmMember, IsOwner


class ExpenseCategoryListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating expense categories.
    """
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExpenseCategory.objects.filter(is_active=True)
    
    
class ExpenseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting expense categories.
    """
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExpenseCategory.objects.all()

    
class ExpenseListView(generics.ListAPIView):
    """
    API endpoint for listing expenses.
    """
    serializer_class = ExpenseListSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = Expense.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(expense_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(expense_date__lte=date_to)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(vendor_name__icontains=search) |
                Q(invoice_number__icontains=search)
            )
        
        return queryset.select_related('category', 'farm', 'recorded_by').order_by('-expense_date', '-created_at')


class ExpenseDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving an expense.
    """
    serializer_class = ExpenseDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = Expense.objects.all()
    

class ExpenseCreateView(generics.CreateAPIView):
    """
    API endpoint for creating an expense.
    """
    serializer_class = ExpenseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class ExpenseUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating an expense.
    """
    serializer_class = ExpenseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Expense.objects.all()
    

class ExpenseDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting an expense.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Expense.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def approve_expense(request, pk):
    """
    API endpoint for approving an expense.
    """
    expense = get_object_or_404(Expense, pk=pk)
    
    expense.status = 'approved'
    expense.approved_by = request.user
    expense.approved_at = timezone.now()
    expense.save()
    
    return Response({'message' : 'Expense approved successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def reject_expense(request, pk):
    """
    API endpoint for rejecting an expense.
    """
    expense = get_object_or_404(Expense, pk=pk)
    
    expense.status = 'rejected'
    expense.save()
    
    return Response({'message': 'Expense rejected successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def mark_expense_paid(request, pk):
    """
    API endpoint for marking an expense as paid.
    """
    expense = get_object_or_404(Expense, pk=pk)
    
    expense.status = 'paid'
    expense.save()
    
    return Response({'message': 'Expense marked as paid.'})


class RecurringExpenseListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating recurring expenses.
    """
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = RecurringExpense.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('category', 'farm').order_by('next_due_date')


class RecurringExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting recurring expenses.
    """
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = RecurringExpense.objects.all()


class ExpenseBudgetListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating expense budgets.
    """
    serializer_class = ExpenseBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = ExpenseBudget.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by period
        period = self.request.query_params.get('period')
        if period:
            queryset = queryset.filter(period=period)
        
        return queryset.select_related('category', 'farm').order_by('-period_start')


class ExpenseBudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting expense budgets.
    """
    serializer_class = ExpenseBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = ExpenseBudget.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expense_stats(request):
    """
    API endpoint for getting expense statistics.
    """
    user = request.user
    farm_id = request.query_params.get('farm')
    
    # Get farms user has access to
    if user.is_owner:
        farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
    else:
        farm_ids = user.farm_memberships.filter(
            is_active=True, status='active'
        ).values_list('farm_id', flat=True)
    
    if farm_id:
        farm_ids = [farm_id] if int(farm_id) in list(farm_ids) else []
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    # Today's expenses
    today_expenses = Expense.objects.filter(
        farm_id__in=farm_ids,
        expense_date=today,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # This week's expenses
    week_expenses = Expense.objects.filter(
        farm_id__in=farm_ids,
        expense_date__gte=week_start,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # This month's expenses
    month_expenses = Expense.objects.filter(
        farm_id__in=farm_ids,
        expense_date__gte=month_start,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # This year's expenses
    year_expenses = Expense.objects.filter(
        farm_id__in=farm_ids,
        expense_date__gte=year_start,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Expenses by category
    expenses_by_category = list(
        Expense.objects.filter(
            farm_id__in=farm_ids,
            expense_date__gte=month_start,
            status='paid'
        ).values('category__name').annotate(
            total=Sum('total_amount')
        ).order_by('-total')
    )
    
    # Expenses by payment method
    expenses_by_payment_method = list(
        Expense.objects.filter(
            farm_id__in=farm_ids,
            expense_date__gte=month_start,
            status='paid'
        ).values('payment_method').annotate(
            total=Sum('total_amount')
        ).order_by('-total')
    )
    
    # Pending expenses
    pending_expenses = Expense.objects.filter(
        farm_id__in=farm_ids,
        status__in=['pending', 'approved']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Top vendors
    top_vendors = list(
        Expense.objects.filter(
            farm_id__in=farm_ids,
            expense_date__gte=month_start,
            status='paid'
        ).values('vendor_name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')[:10]
    )
    
    data = {
        'total_expenses_today': round(today_expenses, 2),
        'total_expenses_this_week': round(week_expenses, 2),
        'total_expenses_this_month': round(month_expenses, 2),
        'total_expenses_this_year': round(year_expenses, 2),
        'expenses_by_category': expenses_by_category,
        'expenses_by_payment_method': expenses_by_payment_method,
        'pending_expenses': round(pending_expenses, 2),
        'top_vendors': top_vendors,
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def budget_comparison(request):
    """
    API endpoint for budget vs actual comparison.
    """
    user = request.user
    farm_id = request.query_params.get('farm')
    period = request.query_params.get('period', 'monthly')
    
    # Get farms user has access to
    if user.is_owner:
        farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
    else:
        farm_ids = user.farm_memberships.filter(
            is_active=True, status='active'
        ).values_list('farm_id', flat=True)
    
    if farm_id:
        farm_ids = [farm_id] if int(farm_id) in list(farm_ids) else []
    
    today = timezone.now().date()
    
    if period == 'monthly':
        period_start = today.replace(day=1)
    elif period == 'quarterly':
        quarter = (today.month - 1) // 3
        period_start = today.replace(month=quarter * 3 + 1, day=1)
    else:  # yearly
        period_start = today.replace(month=1, day=1)
    
    budgets = ExpenseBudget.objects.filter(
        farm_id__in=farm_ids,
        period=period,
        period_start=period_start
    )
    
    data = []
    for budget in budgets:
        utilization = budget.utilization_percentage
        
        if utilization < 75:
            status = 'good'
        elif utilization < 90:
            status = 'warning'
        else:
            status = 'critical'
        
        data.append({
            'budget_id': budget.id,
            'category_name': budget.category.name,
            'budget_amount': budget.budget_amount,
            'spent_amount': budget.spent_amount,
            'remaining_amount': budget.remaining_amount,
            'utilization_percentage': round(utilization, 2),
            'status': status
        })
    
    return Response(data)

