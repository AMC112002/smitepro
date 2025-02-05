from django.contrib import admin
from .models import Item, ItemCategory

# Configuración del admin para las categorías
@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Muestra solo el nombre en la lista
    search_fields = ('name',)  # Permite buscar por nombre


# Configuración del admin para los objetos
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier')  # Muestra nombre, tier y coste
    list_filter = ('tier', 'categories')  # Filtros por tier y categoría
    search_fields = ('name',)  # Permite buscar objetos por nombre
    filter_horizontal = ('categories',)  # Mejor visualización de las categorías en la edición
