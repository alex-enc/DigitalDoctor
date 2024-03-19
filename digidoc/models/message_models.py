from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django import forms

# Create your models here.
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
    birth_year = models.IntegerField(choices=get_birth_year_choices(), verbose_name=("Birth Year"))
    initial_symptoms = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

class MultipleChoice(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
            return self.name
    choice_id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)

class SingleChoice(models.Model):
    label = models.CharField(max_length=100)
    # # is_selected = models.BooleanField(default=False)  # Represents whether the symptom is selected or not
    choice_id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    def __str__(self):
        return self.label

class APIResponse(models.Model):
    conversation_id = models.CharField(max_length=1000)
    scenario = models.CharField(max_length=100)
    phase = models.CharField(max_length=100)
    progress_stage = models.CharField(max_length=100)
    progress_percentage =models.IntegerField()
    step_back_possible = models.BooleanField(default=False)
    has_contraints = models.BooleanField(default=False)
    min_constraints = models.IntegerField(null=True)
    max_constraints = models.IntegerField(null=True)
    question_type = models.CharField(max_length=100, null=True)
    message_type =  models.CharField(max_length=100, null=True)
    mandatory = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)
    def __str__(self):
        return self.conversation_id


class TextInput(models.Model):
    symptom_name = models.CharField(max_length=1000)
    def __str__(self):
        return self.symptom_name

class HealthBackground(models.Model):
    condition_id = models.CharField(max_length=1000)
    def __str__(self):
        return self.condition_id

# class ConversationId(models.Model):
#     conversation_id = models.CharField(max_length=1000)
#     def __str__(self):
#         return self.conversation_id

class Language(models.Model):
    language = models.CharField(max_length=1000)
    language_code = models.CharField(max_length=10)
    def __str__(self):
        return self.language_code
