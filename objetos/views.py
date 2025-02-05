from django.shortcuts import render, get_object_or_404
from .models import Item, ItemCategory

def item_list(request):
    # Filtrar los objetos que tienen la categoría "Consumable" y ordenarlos por precio
    consumables = Item.objects.filter(categories__name__icontains="Consumible").distinct().order_by('price')

    # Filtrar los objetos que NO son consumibles y ordenarlos por precio
    other_items = Item.objects.exclude(id__in=consumables.values_list('id', flat=True)).order_by('price')

    context = {
        'consumables': consumables,
        'other_items': other_items,
    }
    return render(request, 'objetos/item_list.html', context)

def item_detail(request, id):
    # Obtener el objeto mediante su id
    item = get_object_or_404(Item, id=id)
    
    context = {
        'item': item,
    }
    return render(request, 'objetos/item_detail.html', context)