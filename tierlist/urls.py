from django.urls import path
from . import views

urlpatterns = [
    path('community/', views.community_tierlists, name='community_tierlists'),
    path('my/', views.my_tierlists, name='my_tierlists'),
    path('create/', views.create_tierlist, name='create_tierlist'),
    path('<int:pk>/', views.tierlist_detail, name='tierlist_detail'),
    path('edit/<int:pk>/', views.edit_tierlist, name='edit_tierlist'),
    path('delete/<int:pk>/', views.delete_tierlist, name='delete_tierlist'),
]
