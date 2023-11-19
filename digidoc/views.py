from django.shortcuts import render
from .forms import SignUpForm
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def chat(request):
    return render(request, 'chat.html')

def sign_up(request):
    form = SignUpForm()
    return render(request, 'sign_up.html', {'form' : form})

# def sign_up(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('feed')
#     else:
#         form = SignUpForm()
#     return render(request, 'sign_up.html', {'form': form})

