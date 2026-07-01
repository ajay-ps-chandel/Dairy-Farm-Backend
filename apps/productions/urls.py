from django.urls import path
from . import views

urlpatterns = [
    # Milk Production Logs
    path('logs/', views.MilkProductionLogListView.as_view(), name='production-log-list'),
    path('logs/create/', views.MilkProductionLogCreateView.as_view(), name='production-log-create'),
    path('logs/<int:pk>/', views.MilkProductionLogDetailView.as_view(), name='production-log-detail'),
    path('logs/bulk-create/', views.bulk_create_production_logs, name='production-log-bulk-create'),
    
    # Daily Summaries
    path('daily-summaries/', views.DailyProductionSummaryListView.as_view(), name='daily-summary-list'),
    path('daily-summaries/<int:pk>/', views.DailyProductionSummaryDetailView.as_view(), name='daily-summary-detail'),
    
    # Animal Production Summaries
    path('animal-summaries/', views.AnimalProductionSummaryListView.as_view(), name='animal-summary-list'),
    
    # Animal Production History
    path('animals/<int:animal_pk>/history/', views.animal_production_history, name='animal-production-history'),
    
    # Milk Sales
    path('sales/', views.MilkSaleListView.as_view(), name='milk-sale-list'),
    path('sales/<int:pk>/', views.MilkSaleDetailView.as_view(), name='milk-sale-detail'),
    path('sales/<int:pk>/record-payment/', views.record_payment, name='milk-sale-record-payment'),
    
    # Stats
    path('stats/', views.production_stats, name='production-stats'),
    path('sales/stats/', views.milk_sale_stats, name='milk-sale-stats'),
]