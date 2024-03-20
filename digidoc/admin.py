from django.contrib import admin
from digidoc.models.user_models import User 
from digidoc.models.message_models import Message, OnBoarding

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users. """
    list_display = ['username',
                    'first_name',
                    'last_name',
                    'email',
                    'is_active']

@admin.register(Message)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for messages. """
    list_display = ['sender',
                    'content',
                    'timestamp']

@admin.register(OnBoarding)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for messages. """
    list_display = ['name',
                    'birth_year',
                    'initial_symptoms',
                    'gender']