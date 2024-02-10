from django import forms
from django.core.validators import RegexValidator
from digidoc.models.message_models import Message

class SendMessageForm(forms.ModelForm):
    # message = forms.CharField(label="Message DigiDoc")
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'text': forms.Textarea()
        }