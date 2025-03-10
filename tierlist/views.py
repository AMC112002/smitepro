from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from .models import TierList, Tier
from dioses.models import God

class TierListCreateView(LoginRequiredMixin, CreateView):
    model = TierList
    fields = ['name']
    template_name = 'tierlist/tierlist_form.html'
    success_url = reverse_lazy('tierlist_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TierListListView(ListView):
    model = TierList
    template_name = 'tierlist/tierlist_list.html'
    context_object_name = 'tierlists'

class TierListDetailView(DetailView):
    model = TierList
    template_name = 'tierlist/tierlist_detail.html'
