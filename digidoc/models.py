from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    username = models.EmailField(unique=True, blank=False)

class Message(models.Model):
    sender = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

