from django.urls import path
from . import views

urlpatterns = [
    # Expense Categories
    path('categories/', views.ExpenseCategoryListView.as_view(), name='expense-category-list'),
    path('categories/<int:pk>/', views.ExpenseCategoryDetailView.as_view(), name='expense-category-detail'),
    
    # Expenses
    path('', views.ExpenseListView.as_view(), name='expense-list'),
    path('create/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense-update'),
    path('<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense-delete'),
    path('<int:pk>/approve/', views.approve_expense, name='expense-approve'),
    path('<int:pk>/reject/', views.reject_expense, name='expense-reject'),
    path('<int:pk>/mark-paid/', views.mark_expense_paid, name='expense-mark-paid'),
    
    # Recurring Expenses
    path('recurring/', views.RecurringExpenseListView.as_view(), name='recurring-expense-list'),
    path('recurring/<int:pk>/', views.RecurringExpenseDetailView.as_view(), name='recurring-expense-detail'),
    
    # Budgets
    path('budgets/', views.ExpenseBudgetListView.as_view(), name='expense-budget-list'),
    path('budgets/<int:pk>/', views.ExpenseBudgetDetailView.as_view(), name='expense-budget-detail'),
    
    # Stats
    path('stats/', views.expense_stats, name='expense-stats'),
    path('budget-comparison/', views.budget_comparison, name='budget-comparison'),
    
    # Choices
    path('category-types/', views.get_expense_category_types, name='expense-category-types'),
]
