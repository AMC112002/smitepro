from django import forms
from .models import Build
from objetos.models import Item
from dioses.models import God

class BuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = ['god', 'starter_item', 'passive_items', 'relics']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        god_id = kwargs.pop('god_id', None)
        super().__init__(*args, **kwargs)

        # Filtrar objetos iniciales de Tier 2
        self.fields['starter_item'].queryset = Item.objects.filter(
            tier=2,
            categories__name='Inicial'
        )

        # Filtrar objetos pasivos de Tier 3
        if god_id:
            from dioses.models import God
            try:
                selected_god = God.objects.get(id=god_id)
                power_type = selected_god.power

                passive_items = Item.objects.filter(
                    tier=3,
                    categories__name='Objeto Pasivo'
                )

                if power_type == 'Physical':
                    passive_items = passive_items.exclude(
                        categories__name='Poder Mágico'
                    )
                elif power_type == 'Magical':
                    passive_items = passive_items.exclude(
                        categories__name='Poder Físico'
                    )

                self.fields['passive_items'].queryset = passive_items
            except God.DoesNotExist:
                pass
        
        # Filtrar reliquias de Tier 3
        self.fields['relics'].queryset = Item.objects.filter(
            tier=3,
            categories__name='Reliquia'
        )

    def clean_passive_items(self):
        passive_items = self.cleaned_data.get('passive_items')
        print(f"🛠️ Cleaned passive_items: {passive_items}")

        if len(passive_items) != 5:
            raise forms.ValidationError('Debes seleccionar exactamente 5 objetos pasivos.')
        
        return passive_items

    def clean_relics(self):
        relics = self.cleaned_data.get('relics')
        print(f"🛠️ Cleaned relics: {relics}")

        if len(relics) != 2:
            raise forms.ValidationError('Debes seleccionar exactamente 2 reliquias.')

        return relics