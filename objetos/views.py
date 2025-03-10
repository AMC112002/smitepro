from django.shortcuts import render, get_object_or_404
from .models import Item, ItemCategory

def item_list(request):
    # Filtrar los objetos por cada categoría y ordenarlos por precio
    consumables = Item.objects.filter(categories__name__icontains="Consumible").distinct().order_by('price')

    # División de Reliquias
    relics_base = Item.objects.filter(categories__name__icontains="Base").distinct().order_by('price')
    relics_fragment = Item.objects.filter(categories__name__icontains="Fragmento").distinct().order_by('price')
    relics_tier1 = Item.objects.filter(categories__name__icontains="Reliquia", tier=1).distinct().order_by('price')
    relics_tier2 = Item.objects.filter(categories__name__icontains="Reliquia", tier=2).distinct().order_by('price')
    relics_tier3 = Item.objects.filter(categories__name__icontains="Reliquia", tier=3).distinct().order_by('price')

    # División de Iniciales por Tier
    initials_tier1 = Item.objects.filter(categories__name__icontains="Inicial", tier=1).distinct().order_by('price')
    initials_tier2 = Item.objects.filter(categories__name__icontains="Inicial", tier=2).distinct().order_by('price')

    # División de Pasivos por Tier
    passives_tier1 = Item.objects.filter(categories__name__icontains="Objeto Pasivo", tier=1).distinct().order_by('price')
    passives_tier2 = Item.objects.filter(categories__name__icontains="Objeto Pasivo", tier=2).distinct().order_by('price')
    passives_tier3 = Item.objects.filter(categories__name__icontains="Objeto Pasivo", tier=3).distinct().order_by('price')

    context = {
        'consumables': consumables,
        'relics_base': relics_base,
        'relics_fragment': relics_fragment,
        'relics_tier1': relics_tier1,
        'relics_tier2': relics_tier2,
        'relics_tier3': relics_tier3,
        'initials_tier1': initials_tier1,
        'initials_tier2': initials_tier2,
        'passives_tier1': passives_tier1,
        'passives_tier2': passives_tier2,
        'passives_tier3': passives_tier3,
    }
    return render(request, 'objetos/item_list.html', context)

def item_detail(request, id):
    # Obtener el objeto mediante su id
    item = get_object_or_404(Item, id=id)
    
    context = {
        'item': item,
    }
    return render(request, 'objetos/item_detail.html', context)