from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wish
from django.contrib.auth.views import LoginView, LogoutView

class CustomLoginView(LoginView):
    template_name = 'gifts/login.html'
    next_page = 'my_wishes'

class CustomLogoutView(LogoutView):
    template_name = 'gifts/login.html'


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('my_wishes')
    return redirect('login')
            

@login_required
def my_wishes(request):
    return render(request, 'gifts/my-wishes.html')

@login_required
def other_wishes(request):
    return render(request, 'gifts/other-wishes.html')

@login_required
def my_claims(request):
    return render(request, 'gifts/my-claims.html')