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

    