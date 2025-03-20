from django.urls import path
from . import views

urlpatterns = [
    path('', views.stats_home, name='stats_home'),
    path('gods/', views.god_stats, name='god_stats'),
    path('items/', views.item_stats, name='item_stats'),
    path('api/gods-data/', views.api_gods_data, name='api_gods_data'),
    path('api/items-data/', views.api_items_data, name='api_items_data'),
    path('api/builds-timeline/', views.api_builds_timeline, name='api_builds_timeline'),
]