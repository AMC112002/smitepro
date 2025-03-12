from django import forms
from .models import TierList, Tier

class TierListForm(forms.ModelForm):
    class Meta:
        model = TierList
        fields = ['name', 'description', 'is_public']

class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['tier', 'god', 'notes']
