from django.contrib import admin
from .models import Build

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('god', 'user', 'created_at')
    list_filter = ('god', 'user')
