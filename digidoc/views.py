from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def chat(request):
    return render(request, 'chat.html')

