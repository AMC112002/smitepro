from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('gods/', views.gods_by_pantheon, name='gods_by_pantheon'),  # Página de dioses por panteón
    path('god/<int:pk>/', views.GodDetailView.as_view(), name='god_detail'),
]
