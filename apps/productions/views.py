from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    MilkProductionLog, DailyProductionSummary,
    AnimalProductionSummary, MilkSale
)
from .serializers import (
    MilkProductionLogSerializer,
    MilkProductionLogCreateSerializer,
    DailyProductionSummarySerializer,
    AnimalProductionSummarySerializer,
    MilkSaleSerializer,
    MilkSaleUpdateSerializer,
    ProductionStatsSerializer,
    MilkSaleStatsSerializer,
)

from apps.accounts.permissions import IsFarmMember, CanLogProduction, IsOwner
from apps.farms.models import Farm
from apps.animals.models import Animal





class MilkProductionLogListView(generics.ListAPIView):
    """
    Api endpoint for listing milk production logs.
    """
    serializer_class = MilkProductionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        user = self.request.user
        
        # gets farms user has access to
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status ='active'
                ).values_list('farm_id', flat=True)
            
        queryset = MilkProductionLog.objects.filter(farm_id__in=farm_ids)
            
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by animal
        animal_id = self.request.query_params.get('animal')
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by session
        session = self.request.query_params.get('session')
        if session:
            queryset = queryset.filter(session=session)
        
        return queryset.select_related('animal', 'farm', 'recorded_by').order_by('-date', '-created_at')


class MilkProductionLogCreateView(generics.CreateAPIView):
    """
    API endpoint for creating milk production logs.
    """
    serializer_class = MilkProductionLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanLogProduction]


class MilkProductionLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting milk production logs.
    """
    serializer_class = MilkProductionLogSerializer
    permission_classes = [permissions.IsAuthenticated, CanLogProduction]
    queryset = MilkProductionLog.objects.all()
    
    
class DailyProductionSummaryListView(generics.ListAPIView):
    """
    API endpoint for listing daily production summaries.
    """
    serializer_class = DailyProductionSummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = DailyProductionSummary.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.select_related('farm').order_by('-date')


class DailyProductionSummaryDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a daily production summary.
    """
    serializer_class = DailyProductionSummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = DailyProductionSummary.objects.all()


class AnimalProductionSummaryListView(generics.ListAPIView):
    """
    API endpoint for listing animal production summaries.
    """
    serializer_class = AnimalProductionSummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = AnimalProductionSummary.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by animal
        animal_id = self.request.query_params.get('animal')
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        
        # Filter by period type
        period_type = self.request.query_params.get('period_type')
        if period_type:
            queryset = queryset.filter(period_type=period_type)
        
        return queryset.select_related('animal', 'farm').order_by('-period_end')


class MilkSaleListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating milk sales.
    """
    serializer_class = MilkSaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
            ).values_list('farm_id', flat=True)
        
        queryset = MilkSale.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Search by buyer name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(buyer_name__icontains=search)
        
        return queryset.select_related('farm', 'recorded_by').order_by('-date', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class MilkSaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting milk sales.
    """
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = MilkSale.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MilkSaleUpdateSerializer
        return MilkSaleSerializer

