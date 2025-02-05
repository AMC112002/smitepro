from django.shortcuts import render, get_object_or_404
from .models import GameMode

def game_modes_list(request):
    modes = GameMode.objects.all()
    return render(request, 'gamemodes/game_modes_list.html', {'modes': modes})

def game_mode_detail(request, mode_id):
    mode = get_object_or_404(GameMode, id=mode_id)
    
    def should_be_indented(line):
        # Lista de palabras que indican que la línea debe ser indentada
        indent_starters = ['Espíritu', 'Primera', 'Segunda', 'Tercera']
        # Verificar si la línea comienza con un número
        starts_with_number = line.split()[0][0].isdigit() if line.split() else False
        
        return any(line.strip().startswith(word) for word in indent_starters) or starts_with_number
    
    # Procesar las mecánicas únicas
    if mode.unique_gameplay_mechanics:
        mechanics = []
        for line in mode.unique_gameplay_mechanics.split('\n'):
            if line.strip():  # Si la línea no está vacía
                mechanics.append({
                    'text': line,
                    'indent': should_be_indented(line),
                    'empty': False
                })
            else:
                # Añadir líneas vacías sin punto
                mechanics.append({
                    'text': '',
                    'indent': False,
                    'empty': True
                })
    else:
        mechanics = []

    return render(request, 'gamemodes/game_mode_detail.html', {
        'mode': mode,
        'mechanics': mechanics,
    })