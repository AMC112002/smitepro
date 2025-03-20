from django.contrib import admin
from .models import GodStat, ItemStat

@admin.register(GodStat)
class GodStatAdmin(admin.ModelAdmin):
    list_display = ('god', 'usage_count', 'win_rate', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('god__name',)

@admin.register(ItemStat)
class ItemStatAdmin(admin.ModelAdmin):
    list_display = ('item', 'usage_count', 'usage_type', 'win_rate', 'last_updated')
    list_filter = ('usage_type', 'last_updated',)
    search_fields = ('item__name',)