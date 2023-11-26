from django import forms
from .models import User
from django.core.validators import RegexValidator

class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase, a lowercase character and a number.'
        )
            ]
        )
    password_confirmation = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())


    '''Creates new user'''
    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Passwords do not match.')

    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            email = self.cleaned_data.get('email'),
            password = self.cleaned_data.get('new_password')
        )
        return user