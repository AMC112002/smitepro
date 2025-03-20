from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from builds.models import Build
from dioses.models import God
from objetos.models import Item
from .models import GodStat, ItemStat
import json

def stats_home(request):
    """Vista principal de estadísticas"""
    total_builds = Build.objects.filter(is_random=False).count()
    total_gods_used = God.objects.filter(build__is_random=False).distinct().count()
    total_items_used = Item.objects.filter(
        Q(starter_builds__is_random=False) | 
        Q(passive_builds__is_random=False) | 
        Q(relic_builds__is_random=False)
    ).distinct().count()
    
    # Top 5 dioses
    top_gods = God.objects.annotate(
        builds_count=Count('build', filter=Q(build__is_random=False))
    ).order_by('-builds_count')[:5]
    
    # Top 5 objetos iniciales
    top_starters = Item.objects.annotate(
        builds_count=Count('starter_builds', filter=Q(starter_builds__is_random=False))
    ).order_by('-builds_count')[:5]
    
    # Top 5 objetos pasivos
    top_passives = Item.objects.annotate(
        builds_count=Count('passive_builds', filter=Q(passive_builds__is_random=False))
    ).order_by('-builds_count')[:5]
    
    # Top 5 reliquias
    top_relics = Item.objects.annotate(
        builds_count=Count('relic_builds', filter=Q(relic_builds__is_random=False))
    ).order_by('-builds_count')[:5]
    
    context = {
        'total_builds': total_builds,
        'total_gods_used': total_gods_used,
        'total_items_used': total_items_used,
        'top_gods': top_gods,
        'top_starters': top_starters,
        'top_passives': top_passives,
        'top_relics': top_relics,
    }
    
    return render(request, 'stats/stats_home.html', context)

def god_stats(request):
    """Vista de estadísticas de dioses"""
    gods = God.objects.all()
    return render(request, 'stats/god_stats.html', {'gods': gods})

def item_stats(request):
    """Vista de estadísticas de objetos"""
    item_categories = ['Starter', 'Passive', 'Relic']
    return render(request, 'stats/item_stats.html', {'item_categories': item_categories})

def api_gods_data(request):
    try:
        days = request.GET.get('days', None)
        
        # Filtrar las builds por la relación correcta en Build
        build_filter = Q(build__is_random=False)
        if days:
            filter_date = timezone.now() - timedelta(days=int(days))
            build_filter &= Q(build__created_at__gte=filter_date)  # ⭐ Usar build__created_at
        
        print("Ejecutando consulta de dioses...")
        
        gods_data = list(God.objects.annotate(
            builds_count=Count('build', filter=build_filter)  # ⭐ build__is_random
        ).values('name', 'builds_count', 'power'))
        
        print(f"Datos obtenidos: {gods_data[:3] if gods_data else 'No data'}...")
        
        chart_data = {
            'labels': [god['name'] for god in gods_data],
            'datasets': [{
                'label': 'Número de builds',
                'data': [god['builds_count'] for god in gods_data],
                'backgroundColor': [
                    '#FF6384' if god['power'] == 'Magical' else '#36A2EB' 
                    for god in gods_data
                ],
            }]
        }
        
        return JsonResponse(chart_data, safe=False)
    
    except Exception as e:
        print(f"ERROR en api_gods_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def api_items_data(request):
    try:
        category = request.GET.get('category', 'Passive')
        days = request.GET.get('days', None)
        
        # Crear los filtros para las builds usando las relaciones correctas
        build_filter = {}
        if days:
            filter_date = timezone.now() - timedelta(days=int(days))
            if category == 'Starter':
                build_filter['starter_builds__created_at__gte'] = filter_date
            elif category == 'Passive':
                build_filter['passive_builds__created_at__gte'] = filter_date
            elif category == 'Relic':
                build_filter['relic_builds__created_at__gte'] = filter_date
        
        # Añadir el filtro para excluir builds de randomizer
        if category == 'Starter':
            build_filter['starter_builds__is_random'] = False
        elif category == 'Passive':
            build_filter['passive_builds__is_random'] = False
        elif category == 'Relic':
            build_filter['relic_builds__is_random'] = False
        
        # Obtener datos según la categoría
        if category == 'Starter':
            items_data = Item.objects.filter(categories__name='Inicial').annotate(
                builds_count=Count('starter_builds', filter=Q(**build_filter))
            ).values('name', 'builds_count')
        elif category == 'Passive':
            items_data = Item.objects.filter(categories__name='Objeto Pasivo').annotate(
                builds_count=Count('passive_builds', filter=Q(**build_filter))
            ).values('name', 'builds_count')
        elif category == 'Relic':
            items_data = Item.objects.filter(categories__name='Reliquia').annotate(
                builds_count=Count('relic_builds', filter=Q(**build_filter))
            ).values('name', 'builds_count')
        
        # Ordenar y limitar para mejor visualización
        items_data = sorted(items_data, key=lambda x: x['builds_count'], reverse=True)[:15]
        
        # Formatear los datos para las gráficas
        chart_data = {
            'labels': [item['name'] for item in items_data],
            'datasets': [{
                'label': f'Uso de {category}',
                'data': [item['builds_count'] for item in items_data],
                'backgroundColor': [
                    f'hsl({i * 360 // len(items_data)}, 70%, 60%)' for i in range(len(items_data))
                ],
            }]
        }
        
        return JsonResponse(chart_data)
    
    except Exception as e:
        print(f"ERROR en api_items_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def api_builds_timeline(request):
    """API para obtener datos de evolución temporal de builds"""
    # Obtener datos de builds por fecha
    last_30_days = timezone.now() - timedelta(days=30)
    
    builds_by_day = Build.objects.filter(
        created_at__gte=last_30_days,
        is_random=False
    ).extra({
        'day': "date(created_at)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    # Formatear datos para gráfico de línea temporal
    labels = [entry['day'] for entry in builds_by_day]
    data = [entry['count'] for entry in builds_by_day]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Builds creadas',
            'data': data,
            'fill': False,
            'borderColor': '#4bc0c0',
            'tension': 0.1
        }]
    }
    
    return JsonResponse(chart_data)

# Función para actualizar las estadísticas (puede programarse como tarea periódica)
def update_stats():
    """Actualiza las tablas de estadísticas"""
    # Actualizar estadísticas de dioses
    for god in God.objects.all():
        usage_count = Build.objects.filter(god=god, is_random=False).count()
        if usage_count > 0:
            GodStat.objects.update_or_create(
                god=god,
                defaults={
                    'usage_count': usage_count,
                    'last_updated': timezone.now()
                }
            )
    
    # Actualizar estadísticas de objetos iniciales
    for item in Item.objects.filter(starter_builds__isnull=False).distinct():
        usage_count = Build.objects.filter(starter_item=item, is_random=False).count()
        if usage_count > 0:
            ItemStat.objects.update_or_create(
                item=item,
                usage_type='starter',
                defaults={
                    'usage_count': usage_count,
                    'last_updated': timezone.now()
                }
            )
    
    # Actualizar estadísticas de objetos pasivos
    for item in Item.objects.filter(passive_builds__isnull=False).distinct():
        usage_count = Build.objects.filter(passive_items=item, is_random=False).count()
        if usage_count > 0:
            ItemStat.objects.update_or_create(
                item=item,
                usage_type='passive',
                defaults={
                    'usage_count': usage_count,
                    'last_updated': timezone.now()
                }
            )
    
    # Actualizar estadísticas de reliquias
    for item in Item.objects.filter(relic_builds__isnull=False).distinct():
        usage_count = Build.objects.filter(relics=item, is_random=False).count()
        if usage_count > 0:
            ItemStat.objects.update_or_create(
                item=item,
                usage_type='relic',
                defaults={
                    'usage_count': usage_count,
                    'last_updated': timezone.now()
                }
            )