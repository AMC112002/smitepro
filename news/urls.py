from django.urls import path
from .views import news_list, patch_detail, event_detail

urlpatterns = [
    path('', news_list, name='news_list'),
    path('patch/<int:patch_id>/', patch_detail, name='patch_detail'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
]
