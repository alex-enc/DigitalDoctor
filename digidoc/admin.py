from django.contrib import admin
from .models import User, Message

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