from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TierList, Tier, God
from .forms import TierListForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

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
