from django.urls import path
from .views import build_list, my_builds, create_build, build_detail

urlpatterns = [
    path('', build_list, name='build_list'),
    path('my/', my_builds, name='my_builds'),
    path('<int:pk>/', build_detail, name='build_detail'),
    path('create/', create_build, name='create_build'),
]
