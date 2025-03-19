from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Build
from .forms import BuildForm
from dioses.models import God
from objetos.models import Item, ItemCategory

# Mostrar las builds de la comunidad
def build_list(request):
    god_id = request.GET.get('god')
    builds = Build.objects.filter(is_random=False).order_by('-created_at')  # ⭐ Excluir builds randomizer

    if god_id:
        builds = builds.filter(god_id=god_id)

    gods = God.objects.all()

    context = {
        'builds': builds,
        'gods': gods,
    }
    return render(request, 'builds/build_list.html', context)

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)
    return render(request, 'builds/build_detail.html', {'build': build})

# Mostrar tus propias builds
@login_required
def my_builds(request):
    builds = Build.objects.filter(user=request.user).order_by('-created_at')
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