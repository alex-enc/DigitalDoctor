from django.contrib import admin
from digidoc.models.user_models import User 
from digidoc.models.symptom_checker_models import OnBoarding

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users. """
    list_display = ['username',
                    'first_name',
                    'last_name',
                    'email',
                    'is_active']

@admin.register(OnBoarding)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for OnBoarding. """
    list_display = ['name',
                    'birth_year',
                    'initial_symptoms',
                    'gender']