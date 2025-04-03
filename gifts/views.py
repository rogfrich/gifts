from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wish
from .forms import WishForm
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
    context = {
        'wishes': Wish.objects.filter(user=request.user)
    }   

    return render(request, 'gifts/my-wishes.html', context=context)

@login_required
def other_wishes(request):
    return render(request, 'gifts/other-wishes.html')

@login_required
def my_claims(request):
    return render(request, 'gifts/my-claims.html')


@login_required
def create_wish(request):
    if request.method == 'POST':
        form = WishForm(request.POST)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            return redirect('my_wishes')
    else:
        form = WishForm()
    
    context = {
        'form': form
    }

    return render(request, 'gifts/wish-form.html', context=context)