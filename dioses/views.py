from django.shortcuts import render, get_object_or_404
from .models import God
from django.templatetags.static import static
from django.views.generic import DetailView

# Vista para la página de inicio
def home(request):
    return render(request, 'home/home.html')

def gods_by_pantheon(request):
    pantheons = God.PANTHEON_CHOICES
    sorted_gods_by_pantheon = {
        pantheon[1]: God.objects.filter(pantheon=pantheon[0]) for pantheon in sorted(pantheons, key=lambda x: x[1])
    }

    # Diccionario con las imágenes de los panteones
    pantheon_images = {
        pantheon[1]: static(f'panteones/{pantheon[0]}.webp') for pantheon in pantheons
    }

    context = {
        'gods_by_pantheon': sorted_gods_by_pantheon,
        'pantheon_images': pantheon_images,
    }
    return render(request, 'dioses/gods_by_pantheon.html', context)

class GodDetailView(DetailView):
    model = God
    template_name = 'dioses/god_detail.html'  # Nombre del archivo HTML que usará esta vista
    context_object_name = 'god'       # El nombre con el que accederás al objeto en la plantilla

    # Agregar las habilidades relacionadas al contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['abilities'] = self.object.abilities.all()
        return context