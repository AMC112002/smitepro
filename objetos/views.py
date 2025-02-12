from django.shortcuts import render, get_object_or_404
from .models import Item, ItemCategory

def item_list(request):
    # Filtrar los objetos por cada categoría y ordenarlos por precio
    consumables = Item.objects.filter(categories__name__icontains="Consumible").distinct().order_by('price')
    relics = Item.objects.filter(categories__name__icontains="Reliquia").distinct().order_by('price')
    initials = Item.objects.filter(categories__name__icontains="Inicial").distinct().order_by('price')
    passives = Item.objects.filter(categories__name__icontains="Objeto Pasivo").distinct().order_by('price')

    context = {
        'consumables': consumables,
        'relics': relics,
        'initials': initials,
        'passives': passives,
    }
    return render(request, 'objetos/item_list.html', context)

def item_detail(request, id):
    # Obtener el objeto mediante su id
    item = get_object_or_404(Item, id=id)
    
    context = {
        'item': item,
    }
    return render(request, 'objetos/item_detail.html', context)