from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
import random

from dioses.models import God
from objetos.models import Item
from builds.models import Build
from .models import RandomizerHistory
from .forms import RandomizerForm
from django.shortcuts import render, get_object_or_404

@login_required
def randomizer_view(request):
    """Vista principal del randomizer"""
    form = RandomizerForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        # Obtener los filtros del formulario
        pantheon = form.cleaned_data.get('pantheon')
        role = form.cleaned_data.get('role')
        difficulty = form.cleaned_data.get('difficulty')
        
        # Filtrar dioses según los criterios seleccionados
        gods = God.objects.all()
        
        if pantheon:
            gods = gods.filter(pantheon=pantheon)
        if role:
            gods = gods.filter(role=role)
        if difficulty:
            gods = gods.filter(difficulty=difficulty)
            
        if not gods.exists():
            messages.error(request, "No hay dioses disponibles con esos criterios de búsqueda.")
            return redirect('randomizer:randomizer')
        
        # Seleccionar un dios aleatorio
        god = random.choice(list(gods))
        
        # Crear una build aleatoria
        random_build = create_random_build(request.user, god)
        
        # Guardar en el historial
        RandomizerHistory.objects.create(
            user=request.user,
            god=god,
            build=random_build
        )
        
        context = {
            'god': god,
            'build': random_build,
            'form': form
        }
        return render(request, 'randomizer/result.html', context)
    
    context = {
        'form': form,
        'history': RandomizerHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'randomizer/randomizer.html', context)

def create_random_build(user, god):
    """Función para crear una build aleatoria para un dios"""
    
    starters = Item.objects.filter(tier=2, categories__name='Inicial')
    passives = Item.objects.filter(tier=3, categories__name='Objeto Pasivo')
    relics = Item.objects.filter(tier=3, categories__name='Reliquia')

    if god.power == 'Physical':
        passives = passives.exclude(categories__name='Poder Mágico')
    elif god.power == 'Magical':
        passives = passives.exclude(categories__name='Poder Físico')

    if starters.exists() and passives.count() >= 5 and relics.count() >= 2:
        starter_item = random.choice(list(starters))
        passive_items = random.sample(list(passives), 5)
        relic_items = random.sample(list(relics), 2)

        build = Build.objects.create(
            user=user,
            god=god,
            starter_item=starter_item,
            is_random=True  # ⭐ Marcar como build del randomizer
        )
        build.passive_items.add(*passive_items)
        build.relics.add(*relic_items)
        return build
    
    return None

def randomizer_result(request, history_id):
    """Vista para mostrar el resultado detallado de un randomizer pasado"""
    history = get_object_or_404(RandomizerHistory, id=history_id, user=request.user)
    
    context = {
        'god': history.god,
        'build': history.build,
    }
    return render(request, 'randomizer/result.html', context)