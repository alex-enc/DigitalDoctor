from django import forms
from django.core.validators import RegexValidator
from digidoc.models.symptom_checker_models import OnBoarding, MultipleChoice, SingleChoice, TextInput

class OnBoardingForm(forms.ModelForm):
    class Meta:
        model = OnBoarding
        fields = ['name', 'birth_year', 'initial_symptoms']

class MultipleChoiceForm(forms.Form):
    multiple_choices = forms.ModelMultipleChoiceField(queryset=MultipleChoice.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={'class': "list-unstyled"}))

class TextInputForm(forms.ModelForm):
    class Meta:
        model = TextInput
        fields = ['symptom_name']

class SingleChoiceForm(forms.Form):
    choices = forms.ModelChoiceField(queryset=SingleChoice.objects.all(), widget=forms.RadioSelect(attrs={'class': "list-unstyled"}), required=True)

