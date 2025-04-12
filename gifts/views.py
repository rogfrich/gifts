from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Wish
from .forms import WishForm, DeleteWishConfirmationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from urllib.parse import urlencode

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
    User = get_user_model()

    # Get recipient_id from query params
    recipient_id = request.GET.get('recipient_id')

    # Normalize recipient_id (handle None, empty string, or "None")
    try:
        selected_recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        selected_recipient_id = None

    # Get all other users (for dropdown)
    recipients = User.objects.exclude(id=request.user.id)

    # Start with all wishes not created by the current user
    wishes = Wish.objects.exclude(user=request.user)

    # Apply filter if a specific recipient was selected
    if selected_recipient_id is not None:
        wishes = wishes.filter(user__id=selected_recipient_id)

    context = {
        'wishes': wishes,
        'recipients': recipients,
        'selected_recipient_id': selected_recipient_id,
    }

    return render(request, 'gifts/other-wishes.html', context=context)

@login_required
def my_claims(request):
    """
    Get all wishes claimed by the current user
    """
    claims = Wish.objects.filter(claimed=True, claimed_by=request.user.id)


    context = {
        'claims': claims
    }
    return render(request, 'gifts/my-claims.html', context=context)


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

@login_required
def edit_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id, user=request.user)
    if request.method == 'POST':
        form = WishForm(request.POST, instance=wish)
        if form.is_valid():
            form.save()
            return redirect('my_wishes')
    else:
        form = WishForm(instance=wish)
    
    context = {
        'form': form,
    }

    return render(request, 'gifts/wish-form.html', context=context)

@login_required
def delete_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id, user=request.user)
    if request.method == 'POST':
        wish.delete()
        return redirect('my_wishes')
    
    context = {
        'wish': wish,
        'form': DeleteWishConfirmationForm(),
    }
    return render(request, 'gifts/delete-wish.html', context=context)


@require_POST
@login_required
def claim_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id)
    if not wish.claimed and wish.claimed_by is None and wish.user != request.user:
        wish.claimed = True
        wish.claimed_by = request.user
        wish.save()
        return redirect_with_recipient_param(request)

    raise Http404("Wish already claimed or you are the owner of this wish.")
    
@require_POST
@login_required
def unclaim_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id)
    if wish.claimed and wish.claimed_by == request.user:
        wish.claimed = False
        wish.claimed_by = None
        wish.save()
        # Check if a next URL is provided in the POST data (only the case if coming from my_claims)
        if 'next' in request.POST:
            return redirect(request.POST['next'])
        
        # If no next URL is provided, redirect to the default view
        else:
            return redirect_with_recipient_param(request)
    
    raise Http404("Wish not claimed or you are not the claimer of this wish.")

def redirect_with_recipient_param(request, default_view='other_wishes'):
    recipient_id = request.GET.get('recipient_id')
    if recipient_id:
        url = reverse(default_view) + '?' + urlencode({'recipient_id': recipient_id})
    else:
        url = reverse(default_view)
    return redirect(url)