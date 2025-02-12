from django.contrib import admin
from django import forms
from .models import PatchNotes, GodBalance, ItemBalance, Event, AbilityBalance
from dioses.models import God, Ability

class GodBalanceForm(forms.ModelForm):
    class Meta:
        model = GodBalance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Verificar que self.instance existe y tiene un god válido antes de acceder
        if self.instance and hasattr(self.instance, 'god') and self.instance.god is not None:
            self.fields['god'].queryset = God.objects.filter(id=self.instance.god.id)

class GodBalanceAdmin(admin.ModelAdmin):
    form = GodBalanceForm
    list_display = ('god', 'patch', 'change_type')
    list_filter = ('change_type', 'god')

    class Media:
        js = ('admin/js/filter_abilities.js',)  # Cargar script personalizado

class AbilityBalanceForm(forms.ModelForm):
    class Meta:
        model = AbilityBalance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si la instancia existe y tiene un GodBalance asociado con un dios
        if self.instance and hasattr(self.instance, 'god_balance') and self.instance.god_balance is not None:
            god = self.instance.god_balance.god
            if god:
                self.fields['ability'].queryset = Ability.objects.filter(god=god)
            else:
                self.fields['ability'].queryset = Ability.objects.none()  # Si no hay dios, vaciar habilidades

class AbilityBalanceAdmin(admin.ModelAdmin):
    form = AbilityBalanceForm
    list_display = ('ability', 'god_balance', 'change_description')
    list_filter = ('ability',)

    class Media:
        js = ('admin/js/filter_abilities.js',)


admin.site.register(PatchNotes)
admin.site.register(GodBalance, GodBalanceAdmin)
admin.site.register(AbilityBalance, AbilityBalanceAdmin)
admin.site.register(ItemBalance)
admin.site.register(Event)
