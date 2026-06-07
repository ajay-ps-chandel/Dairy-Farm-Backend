from django.urls import path
from . import views

urlpatterns = [
    # Farm CRUD
    path('', views.FarmListView.as_view(), name='farm-list'),
    path('create/', views.FarmCreateView.as_view(), name='farm-create'),
    path('<int:pk>/', views.FarmDetailView.as_view(), name='farm-detail'),
    path('<int:pk>/update/', views.FarmUpdateView.as_view(), name='farm-update'),
    path('<int:pk>/delete/', views.FarmDeleteView.as_view(), name='farm-delete'),
    
    # Farm Settings
    path('<int:pk>/settings/', views.FarmSettingsView.as_view(), name='farm-settings'),
    
    # Farm Documents
    path('<int:farm_pk>/documents/', views.FarmDocumentListView.as_view(), name='farm-document-list'),
    path('<int:farm_pk>/documents/<int:pk>/', views.FarmDocumentDetailView.as_view(), name='farm-document-detail'),
    
    # Farm Notes
    path('<int:farm_pk>/notes/', views.FarmNoteListView.as_view(), name='farm-note-list'),
    path('<int:farm_pk>/notes/<int:pk>/', views.FarmNoteDetailView.as_view(), name='farm-note-detail'),
    
    # Farm Workers
    path('<int:pk>/workers/', views.farm_workers, name='farm-workers'),
    path('<int:pk>/workers/add/', views.add_farm_worker, name='farm-add-worker'),
    path('<int:pk>/workers/remove/', views.remove_farm_worker, name='farm-remove-worker'),
    
    # Stats
    path('stats/', views.farm_stats, name='farm-stats'),
]