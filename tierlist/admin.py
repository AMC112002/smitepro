from django.contrib import admin
from .models import TierList, Tier

@admin.register(TierList)
class TierListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')

@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ('tierlist', 'god', 'tier')
