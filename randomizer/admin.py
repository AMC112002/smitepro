from django.contrib import admin
from django import forms
from .models import RandomizerHistory
from dioses.models import God
from objetos.models import Item

class RandomizerHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'god', 'created_at')
    search_fields = ('user__username', 'god__name')
    list_filter = ('god',)
    date_hierarchy = 'created_at'

admin.site.register(RandomizerHistory, RandomizerHistoryAdmin)