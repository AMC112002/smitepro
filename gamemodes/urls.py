from django.urls import path
from .views import game_modes_list, game_mode_detail

app_name = 'gamemodes'  # This is crucial for the namespace

urlpatterns = [
    path('', game_modes_list, name='game_modes_list'),
    path('<int:mode_id>/', game_mode_detail, name='game_mode_detail'),
]
