from django.urls import path
from .views import TierListCreateView, TierListDetailView, TierListListView

urlpatterns = [
    path('', TierListListView.as_view(), name='tierlist_list'),
    path('crear/', TierListCreateView.as_view(), name='tierlist_create'),
    path('<int:pk>/', TierListDetailView.as_view(), name='tierlist_detail'),
]
