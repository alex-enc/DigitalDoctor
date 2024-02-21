"""digitalDoctor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from digidoc.views import chat_view, home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view.home, name='home'),
    # path('chat/', chat_view.get_chat, name='chat'),
    path('send_symptom_confirmation/', chat_view.send_symptom_confirmation, name='send_symptom_confirmation'),
    path('new_chat/', chat_view.new_chat, name='new_chat'),
    path('on_boarding/', chat_view.send_on_boarding, name='on_boarding'),
    path('chat_choices/', chat_view.send_on_boarding, name='chat_choices'),

]

