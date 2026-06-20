from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import (
    Animal, AnimalHealthRecord, AnimalWeightLog,
    BreedingRecord, CalvingRecord, AnimalNote 
)

from .serializers import (
    AnimalListSerializer,
    AnimalDetailSerializer,
    AnimalCreateSerializer,
    AnimalUpdateSerializer,
    AnimalHealthRecordSerializer,
    AnimalWeightLogSerializer,
    BreedingRecordSerializer,
    CalvingRecordSerializer,
    AnimalNoteSerializer,
    AnimalStatsSerializer,
    AnimalPedigreeSerializer,
)

from apps.accounts.permissions import (
    IsFarmMember, CanManageAnimals, IsOwner
)



class AnimalListView(generics.ListCreateAPIView):
    """
    Listing animals.
    """
    serializer_class = AnimalListSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get farms the user has access to
        if user.is_owner:
            farm_ids = user.owned_farms.filter(is_active=True).values_list('id', flat=True)
        else:
            farm_ids = user.farm_memberships.filter(
                is_active=True, status='active'
                ).values_list('farm_id', flat=True)
            
        queryset = Animal.objects.filter(farm_id__in=farm_ids)
        
        # Filter by farm
        farm_id = self.request.query_params.get('farm')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by species
        species = self.request.query_params.get('species')
        if species:
            queryset = queryset.filter(species=species)
        
        # Filter by breed
        breed = self.request.query_params.get('breed')
        if breed:
            queryset = queryset.filter(breed=breed)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by gender
        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by pregnancy
        pregnant = self.request.query_params.get('pregnant')
        if pregnant is not None:
            queryset = queryset.filter(is_pregnant=pregnant.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(tag_number__icontains=search) |
                Q(name__icontains=search)
            )
        
        return queryset.select_related('farm', 'mother', 'father').order_by('-created_at')


class AnimalDetailView(generics.RetrieveAPIView):
    """
    Retrieve animal details.
    """
    serializer_class = AnimalDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = Animal.objects.all()
    

class AnimalCreateView(generics.CreateAPIView):
    """
    Create a new animal.
    """
    serializer_class = AnimalCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAnimals]
    

class AnimalUpdateView(generics.UpdateAPIView):
    """
    Update an existing animal.
    """
    serializer_class = AnimalUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAnimals]
    queryset = Animal.objects.all()
    
    
class AnimalDeleteView(generics.DestroyAPIView):
    """
    Delete an animal.
    """
    permission_classes = [permissions.IsAuthenticated, CanManageAnimals]
    queryset = Animal.objects.all()
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = 'inactive'
        instance.save()
        
        
class AnimalHealthRecordListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating health records.
    """
    serializer_class = AnimalHealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        animal_id = self.kwargs.get('animal_pk')
        return AnimalHealthRecord.objects.filter(animal_id=animal_id).order_by('-date')
    
    def perform_create(self, serializer):
        animal = get_object_or_404(Animal, pk=self.kwargs['animal_pk'])
        self.check_object_permissions(self.request, animal)
        serializer.save(animal=animal)


class AnimalHealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting health records.
    """
    serializer_class = AnimalHealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = AnimalHealthRecord.objects.all()
    
    
class AnimalWeightLogListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating weight logs.
    """
    serializer_class = AnimalWeightLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    
    def get_queryset(self):
        animal_id = self.kwargs.get('animal_pk')
        return AnimalWeightLog.objects.filter(animal_id=animal_id).order_by('-date')
    
    def perform_create(self, serializer):
        animal = get_object_or_404(Animal, pk=self.kwargs['animal_pk'])
        self.check_object_permissions(self.request, animal)
        serializer.save(animal=animal)
        

class AnimalWeightLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting weight logs.
    """
    serializer_class = AnimalWeightLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmMember]
    queryset = AnimalWeightLog.objects.all()
    
    
