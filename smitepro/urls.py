"""
URL configuration for smitepro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dioses.urls')),  # Redirige la página de inicio a la vista home de la app 'dioses'
    path('accounts/', include('accounts.urls')),  # Redirige las URLs de la app 'accounts' a su archivo urls.py
    path('items/', include('objetos.urls')),  # Redirige las URLs de la app 'objetos' a su archivo urls.py
    path('gamemodes/', include('gamemodes.urls')),  # Redirige las URLs de la app 'gamemodes' a su archivo urls.py
    path('news/', include('news.urls')),  # Redirige las URLs de la app 'news' a su archivo urls.py
    path('tierlist/', include('tierlist.urls')),  # Redirige las URLs de la app 'tierlist' a su archivo urls.py
    path('forum/', include('forum.urls')),  # Redirige las URLs de la app 'forum' a su archivo urls.py
    path('builds/', include('builds.urls')),  # Redirige las URLs de la app 'builds' a su archivo urls.py
    path('randomizer/', include('randomizer.urls')),  # Redirige las URLs de la app 'randomizer' a su archivo urls.py
    path('stats/', include('stats.urls')),  # Redirige las URLs de la app 'stats' a su archivo urls.py
    path('chat/', include('chat.urls')),  # Redirige las URLs de la app 'chat' a su archivo urls.py
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)