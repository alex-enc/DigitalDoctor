from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, date
from django import forms

# Create your models here.
class Message(models.Model):
    sender = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

def get_birth_year_choices():
    current_year = datetime.now().year
    # Calculates the minimum birth year allowed for 16 years old
    start_year = current_year - 100
    end_year = current_year - 16
    # Generates the choices of years from the minimum birth year to the current year
    return [(year, year) for year in range(start_year, end_year+1 )]
class OnBoarding(models.Model):
    GENDER_CHOICES = (('Male','Male'), ('Female','Female'))
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    birth_year = models.IntegerField(choices=get_birth_year_choices(), verbose_name=_("Birth Year"))
    initial_symptoms = models.CharField(max_length=1000)


