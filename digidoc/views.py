from django.shortcuts import render, redirect
from .forms import SignUpForm, LogInForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def home(request):
    return render(request, 'home.html')

def chat(request):
    return render(request, 'chat.html')

# def sign_up(request):
#     form = SignUpForm()
#     return render(request, 'sign_up.html', {'form' : form})

# def login(request):
#     return render(request, 'login.html')

def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            print("Authenticated User:", user)
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or 'chat'
                print("Redirect URL:", redirect_url)
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})

def log_out(request):
    logout(request)
    return redirect('home')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)
            return redirect('chat')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

