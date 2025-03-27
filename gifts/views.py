from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'gifts/homepage.html')


def my_wishes(request):
    return render(request, 'gifts/my-wishes.html')

def other_wishes(request):
    return render(request, 'gifts/other-wishes.html')

def my_claims(request):
    return render(request, 'gifts/my-claims.html')