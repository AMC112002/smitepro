from django.urls import path
from . import views

app_name = 'randomizer'

urlpatterns = [
    path('', views.randomizer_view, name='randomizer'),
    path('result/<int:history_id>/', views.randomizer_result, name='randomizer_result'),
]
