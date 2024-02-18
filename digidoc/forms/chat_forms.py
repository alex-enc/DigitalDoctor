from django import forms
from django.core.validators import RegexValidator
from digidoc.models.message_models import Message, OnBoarding, Symptom

class SendMessageForm(forms.ModelForm):
    # message = forms.CharField(label="Message DigiDoc")
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'text': forms.Textarea()
        }


class OnBoardingForm(forms.ModelForm):
    GENDER_CHOICES = (('Male','Male'), ('Female','Female'))
    class Meta:
        model = OnBoarding
        fields = ['name', 'birth_year', 'initial_symptoms']
    

    gender = forms.ChoiceField(label='Gender:', choices = GENDER_CHOICES, widget = forms.RadioSelect())

class SymptomForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(queryset=Symptom.objects.all(), widget=forms.CheckboxSelectMultiple)



