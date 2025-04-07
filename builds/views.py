from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Build, BuildRating
from .forms import BuildForm, BuildRatingForm
from dioses.models import God
from objetos.models import Item, ItemCategory
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import FloatField
from django.core.paginator import Paginator

# Mostrar las builds de la comunidad
def build_list(request):
    god_id = request.GET.get('god')
    builds = Build.objects.filter(is_random=False).order_by('-created_at')  # Excluir builds randomizer

    if god_id:
        builds = builds.filter(god_id=god_id)

    # Anotación para cálculo de valoración
    from django.db.models import FloatField
    from django.db.models.functions import Coalesce
    from django.db.models import Value, Avg, Count

    builds = builds.annotate(
        avg_rating=Coalesce(Avg('ratings__rating'), Value(0, output_field=FloatField())),  
        rating_count=Count('ratings')
    )

    # Ordenación
    sort_by = request.GET.get('sort', '')
    if sort_by == 'rating':
        builds = builds.order_by('-avg_rating', '-rating_count', '-created_at')

    # 🔹 PAGINACIÓN: 9 builds por página
    paginator = Paginator(builds, 9)
    page_number = request.GET.get('page')
    builds_page = paginator.get_page(page_number)

    gods = God.objects.all()

    context = {
        'builds': builds_page,  # Usar la versión paginada
        'gods': gods,
    }
    return render(request, 'builds/build_list.html', context)

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)
    user_rating = None
    rating_form = None
    
    if request.user.is_authenticated:
        # Verificar si el usuario ya ha valorado esta build
        user_rating = BuildRating.objects.filter(build=build, user=request.user).first()
        
        if request.method == 'POST' and 'rating' in request.POST:
            if user_rating:
                # Actualizar valoración existente
                rating_form = BuildRatingForm(request.POST, instance=user_rating)
            else:
                # Crear nueva valoración
                rating_form = BuildRatingForm(request.POST)
                
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                if not user_rating:
                    rating.build = build
                    rating.user = request.user
                rating.save()
                
                from django.contrib import messages
                messages.success(request, '¡Valoración guardada correctamente!')
                return redirect('build_detail', pk=build.pk)
        else:
            # Mostrar formulario con valoración actual o vacío
            rating_form = BuildRatingForm(instance=user_rating)
    
    # Obtener todas las valoraciones para esta build
    ratings = build.ratings.all()
    
    context = {
        'build': build, 
        'ratings': ratings,
        'user_rating': user_rating,
        'rating_form': rating_form
    }
    return render(request, 'builds/build_detail.html', context)

@login_required
def my_builds(request):
    builds_list = Build.objects.filter(user=request.user, is_random=False).order_by('-created_at')
    paginator = Paginator(builds_list, 5)

    page_number = request.GET.get('page')
    builds = paginator.get_page(page_number)

    context = {'builds': builds}
    return render(request, 'builds/my_builds.html', context)

@login_required
def create_build(request):
    god_id = request.POST.get('god') if request.method == 'POST' else None

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data.setlist('passive_items', request.POST.getlist('passive_items'))
        post_data.setlist('relics', request.POST.getlist('relics'))
        
        print(f"🔎 POST data: {post_data}")

        form = BuildForm(post_data, user=request.user, god_id=god_id)
        if form.is_valid():
            print("✅ Form is valid. Saving build...")
            build = form.save(commit=False)
            build.user = request.user
            build.save()
            form.save_m2m()
            print(f"✅ Build saved with ID: {build.id}")
            return redirect('my_builds')
        else:
            print("❌ Form is NOT valid. Errors:")
            print(form.errors)
    else:
        form = BuildForm(user=request.user, god_id=god_id)

    gods = God.objects.all()

    starter_items = Item.objects.filter(
        tier=2,
        categories__name='Inicial'
    )

    power_type = None
    if god_id:
        try:
            selected_god = God.objects.get(id=god_id)
            power_type = selected_god.power
        except God.DoesNotExist:
            selected_god = None

    passive_items = Item.objects.filter(
        tier=3,
        categories__name='Objeto Pasivo'
    )

    if power_type:
        if power_type == 'Physical':
            magic_item_ids = Item.objects.filter(
                tier=3,
                categories__name='Poder Mágico'
            ).values_list('id', flat=True)
            passive_items = passive_items.exclude(id__in=magic_item_ids)
        elif power_type == 'Magical':
            physical_item_ids = Item.objects.filter(
                tier=3,
                categories__name='Poder Físico'
            ).values_list('id', flat=True)
            passive_items = passive_items.exclude(id__in=physical_item_ids)

    relics = Item.objects.filter(
        tier=3,
        categories__name='Reliquia'
    )

    return render(request, 'builds/create_build.html', {
        'form': form,
        'gods': gods,
        'starter_items': starter_items,
        'passive_items': passive_items,
        'relics': relics,
        'selected_god_id': god_id
    })

@login_required
def edit_build(request, pk):
    build = get_object_or_404(Build, pk=pk)
    
    # Check if the user is the owner of the build
    if build.user != request.user:
        from django.contrib import messages
        messages.error(request, 'No tienes permiso para editar esta build.')
        return redirect('build_detail', pk=build.pk)
    
    god_id = build.god.id
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data.setlist('passive_items', request.POST.getlist('passive_items'))
        post_data.setlist('relics', request.POST.getlist('relics'))
        
        form = BuildForm(post_data, instance=build, user=request.user, god_id=god_id)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, '¡Build actualizada correctamente!')
            return redirect('build_detail', pk=build.pk)
    else:
        form = BuildForm(instance=build, user=request.user, god_id=god_id)
    
    gods = God.objects.all()
    
    starter_items = Item.objects.filter(
        tier=2,
        categories__name='Inicial'
    )
    
    power_type = None
    if god_id:
        try:
            selected_god = God.objects.get(id=god_id)
            power_type = selected_god.power
        except God.DoesNotExist:
            selected_god = None
    
    passive_items = Item.objects.filter(
        tier=3,
        categories__name='Objeto Pasivo'
    )
    
    if power_type:
        if power_type == 'Physical':
            magic_item_ids = Item.objects.filter(
                tier=3,
                categories__name='Poder Mágico'
            ).values_list('id', flat=True)
            passive_items = passive_items.exclude(id__in=magic_item_ids)
        elif power_type == 'Magical':
            physical_item_ids = Item.objects.filter(
                tier=3,
                categories__name='Poder Físico'
            ).values_list('id', flat=True)
            passive_items = passive_items.exclude(id__in=physical_item_ids)
    
    relics = Item.objects.filter(
        tier=3,
        categories__name='Reliquia'
    )
    
    return render(request, 'builds/edit_build.html', {
        'form': form,
        'build': build,
        'gods': gods,
        'starter_items': starter_items,
        'passive_items': passive_items,
        'relics': relics,
        'selected_god_id': god_id
    })

@login_required
def delete_build(request, pk):
    build = get_object_or_404(Build, pk=pk)
    
    # Check if the user is the owner of the build
    if build.user != request.user:
        from django.contrib import messages
        messages.error(request, 'No tienes permiso para eliminar esta build.')
        return redirect('build_detail', pk=build.pk)
    
    if request.method == 'POST':
        build.delete()
        from django.contrib import messages
        messages.success(request, 'Build eliminada correctamente.')
        return redirect('my_builds')
    
    return render(request, 'builds/delete_build.html', {'build': build})