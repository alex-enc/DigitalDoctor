from django import forms
from django.core.validators import RegexValidator
from digidoc.models.message_models import OnBoarding, MultipleChoice, SingleChoice, TextInput

class OnBoardingForm(forms.ModelForm):
    GENDER_CHOICES = (('Male','Male'), ('Female','Female'))
    class Meta:
        model = OnBoarding
        fields = ['name', 'birth_year', 'initial_symptoms']
    

    gender = forms.ChoiceField(label='Gender:', choices = GENDER_CHOICES, widget = forms.RadioSelect())

class MultipleChoiceForm(forms.Form):
    multiple_choices = forms.ModelMultipleChoiceField(queryset=MultipleChoice.objects.all(), widget=forms.CheckboxSelectMultiple)

class TextInputForm(forms.ModelForm):
    class Meta:
        model = TextInput
        fields = ['symptom_name']

# class ChoiceForm(forms.ModelForm):
#     class Meta:
#         model = Choice
#         fields = ['Options:']  # Only include the is_selected field in the form

class SingleChoiceForm(forms.Form):
    # pass
    choices = forms.ModelChoiceField(queryset=SingleChoice.objects.all(), widget=forms.RadioSelect())

# class ConditionForm(forms.Form):
#     conditions = forms.ModelMultipleChoiceField(queryset=Condition.objects.all(), widget=forms.CheckboxSelectMultiple)
