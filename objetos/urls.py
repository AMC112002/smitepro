from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),  # Ruta para listar los objetos
    path('<int:id>/', views.item_detail, name='item_detail'),  # Ruta para los detalles del item
]
