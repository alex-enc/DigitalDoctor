from django import forms
from django.core.validators import RegexValidator
from .models import Message

class SendMessageForm(forms.ModelForm):
    message = forms.CharField(label="Type message")
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'text': forms.Textarea()
        }