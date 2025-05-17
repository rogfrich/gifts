from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import DeleteWishConfirmationForm, WishForm
from .models import Wish


class CustomLoginView(LoginView):
    template_name = "gifts/login.html"
    next_page = "my_wishes"


class CustomLogoutView(LogoutView):
    template_name = "gifts/login.html"


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("my_wishes")
    return redirect("login")


@login_required
def my_wishes(request):
    context = {"wishes": Wish.objects.filter(user=request.user)}

    return render(request, "gifts/my-wishes.html", context=context)


@login_required
def other_wishes(request):
    recipient_id = request.GET.get("recipient_id")
    wishes = []

    if recipient_id:
        try:
            recipient = User.objects.get(pk=recipient_id)
            wishes = Wish.objects.filter(user=recipient).exclude(claimed_by=request.user)
        except User.DoesNotExist:
            recipient = None
    else:
        recipient = None

    context = {
        "recipients": User.objects.exclude(pk=request.user.pk).order_by("username"),
        "selected_recipient": recipient,
        "wishes": wishes,
    }
    return render(request, "gifts/other-wishes.html", context)


@login_required
def my_claims(request):
    """
    Get all wishes claimed by the current user
    """
    claims_by_user = {}
    all_claims = Wish.objects.filter(claimed=True, claimed_by=request.user)
    for user in User.objects.exclude(id=request.user.id).order_by("username"):
        claims_for_this_user = all_claims.filter(user=user)
        if claims_for_this_user.exists():
            claims_by_user[user] = claims_for_this_user

    context = {"claims_by_user": claims_by_user}
    return render(request, "gifts/my-claims.html", context=context)


@login_required
def create_wish(request):
    if request.method == "POST":
        form = WishForm(request.POST)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            return redirect("my_wishes")
    else:
        form = WishForm()

    context = {"form": form}

    return render(request, "gifts/wish-form.html", context=context)


@login_required
def edit_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id, user=request.user)
    if request.method == "POST":
        form = WishForm(request.POST, instance=wish)
        if form.is_valid():
            form.save()
            return redirect("my_wishes")
    else:
        form = WishForm(instance=wish)

    context = {
        "form": form,
    }

    return render(request, "gifts/wish-form.html", context=context)


@login_required
def delete_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id, user=request.user)
    if request.method == "POST":
        wish.delete()
        return redirect("my_wishes")

    context = {
        "wish": wish,
        "form": DeleteWishConfirmationForm(),
    }
    return render(request, "gifts/delete-wish.html", context=context)


@require_POST
@login_required
def claim_wish(request, wish_id):
    wish = get_object_or_404(Wish, id=wish_id)
    if not wish.claimed and wish.claimed_by is None and wish.user != request.user:
        wish.claimed = True
        wish.claimed_by = request.user
        wish.save()
        messages.success(request, f"You claimed '{wish.title}'. You'll find it in 'My Claims'.")
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
        messages.success(request, f"You unclaimed '{wish.title}'.")

        # Check if a next URL is provided in the query string (only the case if coming from my_claims)
        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)

        # If no next URL is provided, redirect to the default view
        else:
            return redirect_with_recipient_param(request)

    raise Http404("Wish not claimed or you are not the claimer of this wish.")


def redirect_with_recipient_param(request, default_view="other_wishes"):
    recipient_id = request.GET.get("recipient_id")
    if recipient_id:
        url = reverse(default_view) + "?" + urlencode({"recipient_id": recipient_id})
    else:
        url = reverse(default_view)
    return redirect(url)
