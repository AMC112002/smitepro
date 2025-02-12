from django.shortcuts import render, get_object_or_404
from .models import PatchNotes, Event, GodBalance, ItemBalance, AbilityBalance

def news_list(request):
    """Lista todas las novedades (patch notes y eventos)"""
    patch_notes = PatchNotes.objects.all().order_by('-publication_date')
    events = Event.objects.all().order_by('-publication_date')
    
    # Combine patch_notes and events, and then order by publication_date
    merged_news = list(patch_notes) + list(events)
    merged_news.sort(key=lambda x: x.publication_date, reverse=True)
    
    return render(request, 'news/news_list.html', {'merged_news': merged_news})

def patch_detail(request, patch_id):
    patch = get_object_or_404(PatchNotes, id=patch_id)

    god_changes = GodBalance.objects.filter(patch=patch).prefetch_related('god')
    ability_changes = AbilityBalance.objects.filter(god_balance__patch=patch).select_related('ability')

    god_buffs = god_changes.filter(change_type='Buff')
    god_nerfs = god_changes.filter(change_type='Nerf')

    item_changes = ItemBalance.objects.filter(patch=patch).prefetch_related('item')
    item_buffs = item_changes.filter(change_type='Buff')
    item_nerfs = item_changes.filter(change_type='Nerf')

    context = {
        'patch': patch,
        'god_buffs': god_buffs,
        'god_nerfs': god_nerfs,
        'ability_changes': ability_changes,
        'item_buffs': item_buffs,
        'item_nerfs': item_nerfs,
    }

    return render(request, 'news/patch_detail.html', context)

def event_detail(request, event_id):
    """Muestra los detalles de un evento"""
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'news/event_detail.html', {'event': event})
