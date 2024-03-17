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
    path('chat/', chat_view.main_chat, name='main_chat'),
    path('send_symptom_confirmation/', chat_view.send_symptom_confirmation, name='send_symptom_confirmation'),
    path('new_chat/', chat_view.new_chat, name='new_chat'),
    path('add_symptom/', chat_view.add_symptom, name='add_symptom'),
    path('autocomplete/', chat_view.autocomplete, name='autocomplete'),
    path('autocomplete_post/', chat_view.autocomplete_post, name='autocomplete_post'),
    path('on_boarding/', chat_view.send_on_boarding, name='on_boarding'),
    path('chat_choices/', chat_view.submit_choice, name='chat_choices'),
    path('health_conditions/', chat_view.send_condition, name='send_health_conditions'),
    path('send_next/', chat_view.send_next, name='send_next'),
    path('send_next2/', chat_view.send_next2, name='send_next2'),
    path('thank_you/', chat_view.thank_you, name='thank_you'),
    path('articles/', chat_view.see_articles, name='articles')

]

