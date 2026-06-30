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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def production_stats(request):
    """
    API endpoint for getting production statistics.
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
    
    # Filter by specific farm if provided
    if farm_id:
        farm_ids = [farm_id] if int(farm_id) in list(farm_ids) else []
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Today's production
    today_production = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date=today
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # This week's production
    week_production = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date__gte=week_start
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # This month's production
    month_production = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date__gte=month_start
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Average daily production (last 30 days)
    last_30_days = today - timedelta(days=30)
    daily_avg = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date__gte=last_30_days
    ).values('date').annotate(daily_total=Sum('quantity')).aggregate(
        avg=Avg('daily_total')
    )['avg'] or 0
    
    # Animals in production (lactating females)
    animals_in_production = Animal.objects.filter(
        farm_id__in=farm_ids,
        gender='female',
        status='lactating',
        is_active=True
    ).count()
    
    # Average per animal
    avg_per_animal = (
        today_production / animals_in_production
        if animals_in_production > 0 else 0
    )
    
    # Top producers (last 7 days)
    last_7_days = today - timedelta(days=7)
    top_producers = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date__gte=last_7_days
    ).values('animal__tag_number', 'animal__name').annotate(
        total=Sum('quantity')
    ).order_by('-total')[:10]
    
    # Production trend (last 14 days)
    last_14_days = today - timedelta(days=14)
    trend = MilkProductionLog.objects.filter(
        farm_id__in=farm_ids,
        date__gte=last_14_days
    ).values('date').annotate(total=Sum('quantity')).order_by('date')
    
    data = {
        'total_production_today': round(today_production, 2),
        'total_production_this_week': round(week_production, 2),
        'total_production_this_month': round(month_production, 2),
        'average_daily_production': round(daily_avg, 2),
        'total_animals_in_production': animals_in_production,
        'average_per_animal': round(avg_per_animal, 2),
        'top_producers': list(top_producers),
        'production_trend': list(trend),
    }
    
    return Response(data)

