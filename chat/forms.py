from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3,
        'placeholder': 'Escribe tu mensaje aquí...',
        'class': 'form-control'
    }), label='')
    
    class Meta:
        model = Message
        fields = ['content']