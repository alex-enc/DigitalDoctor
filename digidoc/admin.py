from django.contrib import admin
from digidoc.models.user_models import User 
from digidoc.models.message_models import OnBoarding

# Register your models here.

@admin.register(OnBoarding)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for messages. """
    list_display = ['name',
                    'birth_year',
                    'initial_symptoms',
                    'gender']