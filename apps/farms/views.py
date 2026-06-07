
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404

from apps.accounts.permissions import IsOwner, IsFarmMember, IsAdminOrOwner
from .models import Farm, FarmDocument, FarmNote, FarmSettings
from .serializers import(
    FarmListSerializer,
    FarmDetailSerializer,
    FarmCreateSerializer,
    FarmUpdateSerializer,
    FarmDocumentSerializer,
    FarmNoteSerializer,
    FarmSettingsSerializer,
    FarmStatsSerializer,
)

class FarmListView(generics.ListAPIView):
    
    serializer_class = FarmListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_owner:
            queryset = Farm.objects.filter(owner=user)
        else:
            # Workers see farms they have membership in
            farm_ids = user.farm_memberships.filter(
                is_active=True,
                status='active'
            ).values_list('farm_id', flat=True)
            queryset = Farm.objects.filter(id__in=farm_ids)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by type
        farm_type = self.request.query_params.get('farm_type')
        if farm_type:
            queryset = queryset.filter(farm_type=farm_type)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(city__icontains=search) |
                Q(state__icontains=search)
            )
        
        return queryset.select_related('owner').order_by('-created_at')
    
class FarmDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a farm.
    """
    serializer_class = FarmDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = Farm.objects.all()
        
class FarmCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a farm.
    Only owners can create farms.
    """
    serializer_class = FarmCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class FarmUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating a farm.
    Only farm owner can update.
    """
    serializer_class = FarmUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Farm.objects.all()
    
class FarmDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a farm.
    Only farm owner can delete (soft delete).
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Farm.objects.all()
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = 'inactive'
        instance.save()

class FarmSettingsView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating farm settings.
    """
    serializer_class = FarmSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_object(self):
        farm = get_object_or_404(Farm, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, farm)
        return farm.settings
    
class FarmDocumentListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating farm documents.
    """
    serializer_class = FarmDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        farm_id = self.kwargs.get('farm_pk')
        return FarmDocument.objects.filter(farm_id=farm_id).order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        farm = get_object_or_404(Farm, pk=self.kwargs['farm_pk'])
        self.check_object_permissions(self.request, farm)
        serializer.save(farm=farm)

class FarmDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting a farm document.
    """
    serializer_class = FarmDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = FarmDocument.objects.all()

class FarmNoteListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating farm notes.
    """
    serializer_class = FarmNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        farm_id = self.kwargs.get('farm_pk')
        queryset = FarmNote.objects.filter(farm_id=farm_id)
        
        # Filter by importance
        important_only = self.request.query_params.get('important')
        if important_only:
            queryset = queryset.filter(is_important=True)
        
        return queryset.order_by('-is_important', '-created_at')
    
    def perform_create(self, serializer):
        farm = get_object_or_404(Farm, pk=self.kwargs['farm_pk'])
        self.check_object_permissions(self.request, farm)
        serializer.save(farm=farm)
        
class FarmNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting a farm note.
    """
    serializer_class = FarmNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = FarmNote.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def farm_stats(request):
    """
    API endpoint for getting farm statistics.
    """
    user = request.user
    
    if user.is_owner:
        farms = Farm.objects.filter(owner=user)
    else:
        farm_ids = user.farm_memberships.filter(
            is_active=True,
            status='active'
        ).values_list('farm_id', flat=True)
        farms = Farm.objects.filter(id__in=farm_ids)
    
    total_farms = farms.count()
    active_farms = farms.filter(status='active').count()
    
    total_animals = farms.aggregate(
        total=Sum('current_animals')
    )['total'] or 0
    
    total_capacity = farms.aggregate(
        total=Sum('max_animals')
    )['total'] or 0
    
    capacity_utilization = (
        (total_animals / total_capacity * 100) if total_capacity > 0 else 0
    )
    
    farms_by_type = dict(
        farms.values('farm_type').annotate(
            count=Count('id')
        ).values_list('farm_type', 'count')
    )
    
    farms_by_status = dict(
        farms.values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count')
    )
    
    data = {
        'total_farms': total_farms,
        'active_farms': active_farms,
        'total_animals': total_animals,
        'total_capacity': total_capacity,
        'capacity_utilization': round(capacity_utilization, 2),
        'farms_by_type': farms_by_type,
        'farms_by_status': farms_by_status,
    }
    
    serializer = FarmStatsSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def add_farm_worker(request, pk):
    """
    API endpoint for adding a worker to a farm.
    """
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    
    worker_id = request.data.get('worker_id')
    permissions_data = {
        'can_add_animals': request.data.get('can_add_animals', False),
        'can_edit_animals': request.data.get('can_edit_animals', False),
        'can_delete_animals': request.data.get('can_delete_animals', False),
        'can_log_production': request.data.get('can_log_production', True),
        'can_manage_inventory': request.data.get('can_manage_inventory', False),
        'can_view_reports': request.data.get('can_view_reports', False),
        'can_manage_expenses': request.data.get('can_manage_expenses', False),
    }
    
    from apps.accounts.models import FarmMembership, User
    
    try:
        worker = User.objects.get(pk=worker_id, role='worker', is_active=True)
    except User.DoesNotExist:
        return Response(
            {'error': 'Worker not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    membership, created = FarmMembership.objects.update_or_create(
        user=worker,
        farm=farm,
        defaults={
            'status': 'active',
            'is_active': True,
            **permissions_data
        }
    )
    
    return Response(
        {
            'message': 'Worker added to farm successfully.',
            'created': created
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def remove_farm_worker(request, pk):
    """
    API endpoint for removing a worker from a farm.
    """
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    
    worker_id = request.data.get('worker_id')
    
    from apps.accounts.models import FarmMembership
    
    try:
        membership = FarmMembership.objects.get(
            user_id=worker_id,
            farm=farm
        )
        membership.status = 'left'
        membership.is_active = False
        membership.save()
        
        return Response(
            {'message': 'Worker removed from farm successfully.'},
            status=status.HTTP_200_OK
        )
    except FarmMembership.DoesNotExist:
        return Response(
            {'error': 'Worker is not a member of this farm.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def farm_workers(request, pk):
    """
    API endpoint for listing workers of a farm.
    """
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    
    from apps.accounts.models import FarmMembership
    
    memberships = FarmMembership.objects.filter(
        farm=farm,
        is_active=True,
        status='active'
    ).select_related('user')
    
    data = []
    for membership in memberships:
        data.append({
            'id': membership.user.id,
            'email': membership.user.email,
            'full_name': membership.user.full_name,
            'phone': membership.user.phone,
            'designation': membership.user.designation,
            'joined_at': membership.joined_at,
            'permissions': {
                'can_add_animals': membership.can_add_animals,
                'can_edit_animals': membership.can_edit_animals,
                'can_delete_animals': membership.can_delete_animals,
                'can_log_production': membership.can_log_production,
                'can_manage_inventory': membership.can_manage_inventory,
                'can_view_reports': membership.can_view_reports,
                'can_manage_expenses': membership.can_manage_expenses,
            }
        })
    
    return Response(data)