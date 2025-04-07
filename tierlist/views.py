from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TierList, Tier, God
from .forms import TierListForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

# Vista para las tierlists de la comunidad
def community_tierlists(request):
    search_query = request.GET.get('search', '')
    
    # Filtro base: tierlists públicas
    tierlists = TierList.objects.filter(is_public=True).order_by('-created_at')
    
    # Aplicar búsqueda si hay una consulta
    if search_query:
        tierlists = tierlists.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(tierlists, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tierlists': page_obj, 
        'title': 'Tier Lists de la Comunidad',
        'search_query': search_query  # Enviar query a la plantilla
    }
    
    # Para solicitudes AJAX, renderizar un template parcial
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'tierlist/includes/tierlist_results.html', context)
    
    # Renderizado normal para solicitudes regulares
    return render(request, 'tierlist/community_tierlists.html', context)

# Vista para las tierlists del usuario logueado
@login_required
def my_tierlists(request):
    search_query = request.GET.get('search', '')
    
    # Filtro base: tierlists del usuario logueado
    tierlists = TierList.objects.filter(user=request.user).order_by('-created_at')
    
    # Aplicar búsqueda si hay una consulta
    if search_query:
        tierlists = tierlists.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(tierlists, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tierlists': page_obj, 
        'title': 'Mis Tier Lists',
        'search_query': search_query  # Enviar query a la plantilla
    }
    
    # Para solicitudes AJAX, renderizar un template parcial
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'tierlist/includes/tierlist_results.html', context)
    
    # Renderizado normal para solicitudes regulares
    return render(request, 'tierlist/my_tierlists.html', context)

# Vista para crear una tierlist
@login_required
def create_tierlist(request):
    if request.method == 'POST':
        form = TierListForm(request.POST)
        if form.is_valid():
            tierlist = form.save(commit=False)
            tierlist.user = request.user
            tierlist.save()

            # Procesar los dioses en los tiers
            for key, value in request.POST.items():
                if key.startswith('god_tier_'):
                    try:
                        god_id = key.replace('god_tier_', '')
                        tier_name = value
                        god = God.objects.get(id=god_id)
                        
                        # Crear la relación Tier
                        Tier.objects.create(
                            tierlist=tierlist,
                            tier=tier_name,
                            god=god
                        )
                    except (God.DoesNotExist, ValueError) as e:
                        print(f"Error procesando dios {god_id} para tier {tier_name}: {e}")
            
            messages.success(request, 'Tu Tier List ha sido creada con éxito.')
            return redirect(tierlist.get_absolute_url())
    else:
        form = TierListForm()
    
    gods = God.objects.all().order_by('name')
    
    return render(
        request,
        'tierlist/create_tierlist.html',
        {
            'form': form,
            'gods': gods,
            'title': 'Crear Tier List'
        }
    )

# Vista para la visualización de una tierlist
@login_required
def tierlist_detail(request, pk):
    tierlist = TierList.objects.get(pk=pk)
    tiers = Tier.objects.filter(tierlist=tierlist).select_related('god')
    
    # Lista de nombres de tiers
    tier_names = ['S', 'A', 'B', 'C', 'D', 'F']

    context = {
        'tierlist': tierlist,
        'tiers': tiers,
        'tier_names': tier_names,  
    }
    
    return render(request, 'tierlist/tierlist_detail.html', context)

@login_required
def edit_tierlist(request, pk):
    tierlist = get_object_or_404(TierList, pk=pk)
    
    # Verificar que el usuario sea el propietario
    if request.user != tierlist.user:
        return HttpResponseForbidden("No tienes permiso para editar esta Tier List.")
    
    # Obtener los tiers actuales
    existing_tiers = Tier.objects.filter(tierlist=tierlist).select_related('god')
    
    if request.method == 'POST':
        form = TierListForm(request.POST, instance=tierlist)
        if form.is_valid():
            form.save()
            
            # Eliminar todos los tiers existentes
            Tier.objects.filter(tierlist=tierlist).delete()
            
            # Procesar los dioses en los tiers
            for key, value in request.POST.items():
                if key.startswith('god_tier_'):
                    try:
                        god_id = key.replace('god_tier_', '')
                        tier_name = value
                        god = God.objects.get(id=god_id)
                        
                        # Crear la relación Tier
                        Tier.objects.create(
                            tierlist=tierlist,
                            tier=tier_name,
                            god=god
                        )
                    except (God.DoesNotExist, ValueError) as e:
                        print(f"Error procesando dios {god_id} para tier {tier_name}: {e}")
            
            messages.success(request, 'Tu Tier List ha sido actualizada con éxito.')
            return redirect(tierlist.get_absolute_url())
    else:
        form = TierListForm(instance=tierlist)
    
    # Crear un diccionario de asignaciones actuales (god_id: tier)
    current_assignments = {str(tier.god.id): tier.tier for tier in existing_tiers}
    
    # Obtener todos los dioses
    gods = God.objects.all().order_by('name')
    
    return render(
        request,
        'tierlist/edit_tierlist.html',
        {
            'form': form,
            'tierlist': tierlist,
            'gods': gods,
            'current_assignments': current_assignments,
            'title': 'Editar Tier List'
        }
    )

# Vista para eliminar una tierlist
@login_required
def delete_tierlist(request, pk):
    tierlist = get_object_or_404(TierList, pk=pk)
    
    # Verificar que el usuario sea el propietario
    if request.user != tierlist.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta Tier List.")
    
    if request.method == 'POST':
        # Eliminar la tierlist
        tierlist_name = tierlist.name
        tierlist.delete()
        messages.success(request, f'Tu Tier List "{tierlist_name}" ha sido eliminada.')
        return redirect('my_tierlists')
    
    return render(
        request,
        'tierlist/delete_tierlist.html',
        {
            'tierlist': tierlist,
            'title': 'Eliminar Tier List'
        }
    )
